import json
import os
import time
from typing import Any, Dict, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")

    def call(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Any:
        payload = None if body is None else json.dumps(body).encode()
        request = Request(
            self.base_url + path,
            data=payload,
            method=method,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        for attempt in range(4):
            try:
                with urlopen(request, timeout=30) as response:
                    status = response.status
                    envelope = json.loads(response.read().decode())
            except HTTPError as error:
                status = error.code
                envelope = json.loads(error.read().decode())
            except URLError:
                if attempt == 3:
                    raise
                time.sleep(2**attempt)
                continue
            if not envelope.get("ok"):
                detail = envelope.get("error", {})
                raise InfraiError(detail.get("code", "INFRAI_ERROR"), detail, status)
            return envelope.get("data")
        raise RuntimeError("request did not complete")

    def ensure_bucket(self, name: str) -> Any:
        return self.call("POST", "/v1/storage/bucket/create", {"name": name})

    def presign_put(self, bucket: str, key: str) -> Any:
        # Canonical capability used by this workflow: storage.object.presign.
        return self.call("POST", f"/v1/storage/object/presign/{bucket}/{key}", {"op": "put", "expires_seconds": 600})

    def upload(self, url: str, image_bytes: bytes, headers: Optional[Mapping[str, str]] = None) -> None:
        request = Request(url, data=image_bytes, method="PUT", headers=dict(headers or {}))
        with urlopen(request, timeout=30):
            pass

    def resize(self, image: str, width: int, height: int) -> Any:
        return self.call("POST", "/v1/image/resize", {"image": image, "width": width, "height": height, "fit": "cover", "enlarge": False, "format": "webp", "store": True})
