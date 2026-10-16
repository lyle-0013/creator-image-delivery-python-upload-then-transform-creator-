from content_delivery import CreatorUpload, publish_variant, updates_for_subscribers


class RecordingClient:
    def __init__(self):
        self.calls = []

    def ensure_bucket(self, bucket):
        self.calls.append(("bucket", bucket))

    def presign_put(self, bucket, key):
        self.calls.append(("presign", bucket, key))
        return {"url": "https://uploads.example/image", "headers": {"Content-Type": "image/jpeg"}}

    def upload(self, url, image_bytes, headers):
        self.calls.append(("upload", url, image_bytes, headers))

    def resize(self, image, width, height):
        self.calls.append(("resize", image, width, height))
        return {"url": "https://cdn.example/image.webp"}


def test_upload_completes_before_resize():
    client = RecordingClient()

    result = publish_variant(CreatorUpload("maker-7", "cover.jpg"), b"image data", client)

    assert [call[0] for call in client.calls] == ["bucket", "presign", "upload", "resize"]
    assert client.calls[2] == (
        "upload",
        "https://uploads.example/image",
        b"image data",
        {"Content-Type": "image/jpeg"},
    )
    assert result["variant"]["url"].endswith("image.webp")


def test_subscribers_receive_the_published_variant():
    upload = CreatorUpload("maker-7", "cover.jpg")
    updates = updates_for_subscribers(["sub-a", "sub-b"], "https://cdn.example/cover.webp")
    assert upload.creator_id == "maker-7"
    assert [item.subscriber_id for item in updates] == ["sub-a", "sub-b"]
    assert all(item.variant_url.endswith("cover.webp") for item in updates)
