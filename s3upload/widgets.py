from __future__ import annotations

import os
from typing import Any
from urllib.parse import unquote_plus as urlunquote_plus

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.forms import widgets
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe

from .utils import (
    get_bucket_endpoint_url,
    get_s3_path_from_url,
    get_signed_download_url,
)


class S3UploadWidget(widgets.TextInput):
    class Media:
        js = ("s3upload/js/django-s3-uploads.min.js",)
        css = {
            "all": (
                "s3upload/css/bootstrap-progress.min.css",
                "s3upload/css/styles.css",
            )
        }

    def __init__(self, dest: str, **kwargs: Any) -> None:
        if not dest:
            raise ValueError("S3UploadWidget must be initialised with a destination")
        if dest not in settings.S3UPLOAD_DESTINATIONS:
            raise ImproperlyConfigured(
                "S3UploadWidget destination '%s' is not configured. "
                "Please check settings.S3UPLOAD_DESTINATIONS." % dest
            )
        self.acl = settings.S3UPLOAD_DESTINATIONS[dest].get("acl", "public-read")
        self.dest = dest
        super(S3UploadWidget, self).__init__(**kwargs)

    def get_file_url(self, value: str) -> str:
        if value:
            bucket_name = settings.S3UPLOAD_DESTINATIONS[self.dest].get("bucket")
            if self.acl == "private":
                return get_signed_download_url(value, bucket_name)
            else:
                # Default to virtual-hosted–style URL
                bucket_url = get_bucket_endpoint_url(bucket_name)
                return "{}/{}".format(bucket_url, value)
        else:
            return ""

    def get_attr(
        self, attrs: dict[str, Any] | None, key: str, default: str = ""
    ) -> str:
        return self.build_attrs(attrs).get(key, default) if attrs else default

    def render(
        self, name: str, value: str, attrs: dict[str, Any] | None = None, **kwargs: Any
    ) -> str:
        path = get_s3_path_from_url(value) if value else ""
        file_name = os.path.basename(urlunquote_plus(path))
        tpl = os.path.join("s3upload", "s3upload-widget.tpl")
        output = render_to_string(
            tpl,
            {
                "policy_url": reverse("s3upload"),
                "element_id": self.get_attr(attrs, "id"),
                "file_name": file_name,
                "dest": self.dest,
                "file_url": self.get_file_url(path),
                "name": name,
                "style": self.get_attr(attrs, "style"),
            },
        )
        # TODO: review use of mark_safe - will the template render
        # cover cases of bad filenames?
        return mark_safe(output)  # noqa: S703, S308
