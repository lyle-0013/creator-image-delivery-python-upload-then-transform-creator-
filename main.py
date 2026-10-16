import argparse
import json

from content_delivery import CreatorUpload, publish_variant, updates_for_subscribers
from infrai_client import InfraiClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish a creator image variant")
    parser.add_argument("creator_id")
    parser.add_argument("filename")
    parser.add_argument("--subscriber", action="append", default=[])
    args = parser.parse_args()
    with open(args.filename, "rb") as image_file:
        image_bytes = image_file.read()
    result = publish_variant(CreatorUpload(args.creator_id, args.filename), image_bytes, InfraiClient())
    variant = result["variant"]
    variant_url = variant.get("url") if isinstance(variant, dict) else str(variant)
    result["subscriber_updates"] = [u.__dict__ for u in updates_for_subscribers(args.subscriber, variant_url)]
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
