import pytest

from django.conf import settings
from django.test import TestCase

from s3upload.utils import get_s3_path_from_url


BUCKET = settings.AWS_STORAGE_BUCKET_NAME
PATH = "folder1/folder2/file1.json"

@pytest.mark.parametrize(
    "url",
    [
        f"s3://{BUCKET}/{PATH}",
        f"https://{BUCKET}.s3.aws-region.amazonaws.com/{PATH}?test=1&test1=2",
        f"https://{BUCKET}.s3.amazonaws.com:443/{PATH}",
        f"https://s3-aws-region.amazonaws.com/{BUCKET}/{PATH}",
        f"https://s3-aws-region.amazonaws.com:443/{BUCKET}/{PATH}",
        f"https%3a%2f%2fs3-aws-region.amazonaws.com%3a443%2f{BUCKET}%2ffolder1%2ffolder2%2ffile1.json"
    ]
)
def test_get_s3_path_from_url(url: str) -> None:
    assert get_s3_path_from_url(url) == PATH
