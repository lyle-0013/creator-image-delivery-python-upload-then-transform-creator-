from dataclasses import dataclass
from typing import Any, Dict, List

from infrai_client import InfraiClient


@dataclass(frozen=True)
class CreatorUpload:
    creator_id: str
    filename: str
    width: int = 1200
    height: int = 1200


@dataclass(frozen=True)
class SubscriberUpdate:
    subscriber_id: str
    variant_url: str


def publish_variant(
    upload: CreatorUpload, image_bytes: bytes, client: InfraiClient, bucket: str = "creator-assets"
) -> Dict[str, Any]:
    """Prepare a direct upload and its resized delivery variant."""
    client.ensure_bucket(bucket)
    key = f"{upload.creator_id}/{upload.filename}"
    signed = client.presign_put(bucket, key)
    source = signed["url"]
    client.upload(source, image_bytes, signed.get("headers"))
    resized = client.resize(source, upload.width, upload.height)
    return {"key": key, "upload_url": source, "variant": resized}


def updates_for_subscribers(subscribers: List[str], variant_url: str) -> List[SubscriberUpdate]:
    return [SubscriberUpdate(subscriber_id=item, variant_url=variant_url) for item in subscribers]
