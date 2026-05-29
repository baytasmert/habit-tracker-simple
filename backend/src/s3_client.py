"""LocalStack S3 client - habit progress photo upload/list."""
import boto3
from botocore.exceptions import ClientError

from .config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.aws_endpoint_url,
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def ensure_bucket() -> None:
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.s3_bucket)
    except ClientError:
        client.create_bucket(Bucket=settings.s3_bucket)


def upload_photo(key: str, body: bytes, content_type: str = "image/jpeg") -> str:
    ensure_bucket()
    client = get_s3_client()
    client.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=body,
        ContentType=content_type,
    )
    return f"s3://{settings.s3_bucket}/{key}"


def list_photos(prefix: str) -> list[str]:
    client = get_s3_client()
    try:
        resp = client.list_objects_v2(Bucket=settings.s3_bucket, Prefix=prefix)
    except ClientError:
        return []
    return [obj["Key"] for obj in resp.get("Contents", [])]


def get_photo(key: str):
    """S3'ten foto byte'larını + content-type döner. Backend içeriden
    (localstack:4566) erişebildiği için tarayıcıya stream edebiliriz."""
    client = get_s3_client()
    obj = client.get_object(Bucket=settings.s3_bucket, Key=key)
    return obj["Body"].read(), obj.get("ContentType", "image/jpeg")
