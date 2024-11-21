from __future__ import annotations

import hashlib
import hmac
import json
from base64 import b64encode
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import unquote, urlparse

import boto3
from django.conf import settings


def create_upload_data(  # noqa: C901
    *,
    content_type: str,
    key: str,
    acl: str,
    bucket: str | None = None,
    cache_control: str | None = None,
    content_disposition: str | None = None,
    content_length_range: str | None = None,
    server_side_encryption: str | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    """Generate AWS upload payload."""
    access_key = settings.AWS_ACCESS_KEY_ID
    secret_access_key = settings.AWS_SECRET_ACCESS_KEY
    bucket = bucket or settings.AWS_STORAGE_BUCKET_NAME
    region = settings.S3UPLOAD_REGION
    bucket_url = get_bucket_endpoint_url(bucket, region)
    expires_in = datetime.utcnow() + timedelta(seconds=60 * 5)
    expires = expires_in.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    now_date = datetime.utcnow().strftime("%Y%m%dT%H%M%S000Z")
    raw_date = datetime.utcnow().strftime("%Y%m%d")

    policy_dict: dict[str, Any] = {
        "expiration": expires,
        "conditions": [
            {"bucket": bucket},
            {"acl": acl},
            ["starts-with", "$key", ""],
            {"success_action_status": "201"},
            {"x-amz-credential": f"{access_key}/{raw_date}/{region}/s3/aws4_request"},
            {"x-amz-algorithm": "AWS4-HMAC-SHA256"},
            {"x-amz-date": now_date},
            {"content-type": content_type},
        ],
    }

    if token:
        policy_dict["conditions"].append({"x-amz-security-token": token})

    if cache_control:
        policy_dict["conditions"].append({"Cache-Control": cache_control})

    if content_disposition:
        policy_dict["conditions"].append({"Content-Disposition": content_disposition})

    if server_side_encryption:
        policy_dict["conditions"].append(
            {"x-amz-server-side-encryption": server_side_encryption}
        )

    if content_length_range:
        policy_dict["conditions"].append(
            ["content-length-range", content_length_range[0], content_length_range[1]]
        )

    policy_object = json.dumps(policy_dict)

    policy = b64encode(policy_object.replace("\n", "").replace("\r", "").encode())

    date_key = hmac.new(
        b"AWS4" + secret_access_key.encode("utf-8"),
        msg=raw_date.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()

    date_region_key = hmac.new(
        date_key, msg=region.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()

    date_region_service_key = hmac.new(
        date_region_key, msg=b"s3", digestmod=hashlib.sha256
    ).digest()

    signing_key = hmac.new(
        date_region_service_key, msg=b"aws4_request", digestmod=hashlib.sha256
    ).digest()

    signature = hmac.new(signing_key, msg=policy, digestmod=hashlib.sha256).hexdigest()
    return_dict = {
        "policy": policy.decode(),  # decode to make it JSON serializable
        "success_action_status": 201,
        "x-amz-credential": f"{access_key}/{raw_date}/{region}/s3/aws4_request",
        "x-amz-date": now_date,
        "x-amz-signature": signature,
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "form_action": bucket_url,
        "key": key,
        "acl": acl,
        "content-type": content_type,
    }

    if token:
        return_dict["x-amz-security-token"] = token

    if server_side_encryption:
        return_dict["x-amz-server-side-encryption"] = server_side_encryption

    if cache_control:
        return_dict["Cache-Control"] = cache_control

    if content_disposition:
        return_dict["Content-Disposition"] = content_disposition

    return return_dict


def get_s3_path_from_url(
    url: str, bucket_name: str = settings.AWS_STORAGE_BUCKET_NAME
) -> str:
    decoded = unquote(url)
    path = urlparse(decoded).path

    # The bucket name might be part of the path,
    # so get the path that comes after the bucket name
    key_path = path.split(bucket_name)[-1]

    # Remove slash prefix if present
    if key_path[0] == "/":
        key_path = key_path[1:]

    return key_path


def get_signed_download_url(
    key: str,
    bucket_name: str | None = None,
    ttl: int = 60,
) -> str:
    bucket_name = bucket_name or settings.AWS_STORAGE_BUCKET_NAME
    bucket_endpoint = get_bucket_endpoint_url(bucket_name)

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=bucket_endpoint,
    )
    download_url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": bucket_name, "Key": key}, ExpiresIn=ttl
    )
    return download_url


# virtual-hosted-style URLs are now the default
# Example: https://bucket-name.s3.Region.amazonaws.com/key name
# See: https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-bucket-intro.html
def get_bucket_endpoint_url(
    bucket_name: str | None = None,
    region: str | None = None,
    default: str = "https://{bucket}.s3.{region}.amazonaws.com",
) -> str:
    bucket_name = bucket_name or settings.AWS_STORAGE_BUCKET_NAME
    region = region or settings.S3UPLOAD_REGION
    bucket_endpoint = getattr(
        settings,
        "S3UPLOAD_BUCKET_ENDPOINT",
        default,
    )
    return bucket_endpoint.format(bucket=bucket_name, region=region)
