"""Sample integration test proving S3 is mocked with moto (no real AWS)."""

from collections.abc import Generator

import boto3
import pytest
from moto import mock_aws


@pytest.fixture
def s3_bucket() -> Generator[str, None, None]:
    """Provide a mocked S3 bucket, with moto intercepting all AWS calls.

    Yields:
        The name of the created (mocked) bucket.
    """
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="loja-club-test")
        yield "loja-club-test"


def test_s3_put_get_is_mocked(s3_bucket: str) -> None:
    """Put and read back an object on the mocked bucket, hitting no real AWS.

    Args:
        s3_bucket: Name of the mocked S3 bucket.
    """
    client = boto3.client("s3", region_name="us-east-1")
    client.put_object(Bucket=s3_bucket, Key="hello.txt", Body=b"loja club")
    body = client.get_object(Bucket=s3_bucket, Key="hello.txt")["Body"].read()
    assert body == b"loja club"
