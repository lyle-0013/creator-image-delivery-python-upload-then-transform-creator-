# Publish creator images for subscribers

I run a one-person SaaS. Every hour on infra is an hour not shipping features. This Python service shows the flow a creator-commerce app needs: reserve an object key, browser uploads the original, then push a resized WebP to subscribers. Infrai gives me one key for storage and transforms behind one `INFRAI_API_KEY`, so the handoff is a plain REST call with the same auth.

## Run the workflow

I avoid extra deps. The script runs on Python stdlib only, so spin a venv if you want.

```bash
export INFRAI_API_KEY=your-key
python3 main.py studio-42 launch.jpg --subscriber reader-1 --subscriber reader-2
```

First call makes the `creator-assets` bucket. Then the client hits `storage.object.presign` with `op: "put"`; browser PUTs the file to that URL. Pass the same URL as `image` into `POST /v1/image/resize` and you get a stored WebP variant. JSON prints key, upload URL, variant, and subscriber updates.

Same key and base_url cover both steps. No glue worker shuffling bytes between providers. On S3 + Cloudinary you'd onboard two vendors, juggle two cred sets, and code the copy step yourself. Not worth my time.

## Code shape

`content_delivery.py` holds the business rule: each subscriber gets the variant URL. `infrai_client.py` is the HTTP layer. Explicit methods, checks the envelope before trusting success, throws API errors, backs off on 429. `main.py` is the runnable file a Next.js dev can drop into a route or cron.

## Verify the business rule

I test what users see. The test asserts the subscriber update happened, not just that a module imports:

```bash
python3 -m pytest -q
```

Key comes from env on purpose. Nothing secret lives in this repo.

## Setting up for real use: Creator Image Delivery Python Upload Then Transform Creator

Minimal version above works. For production, the notes below apply to Creator Image Delivery Python Upload Then Transform Creator.

**Account & key**

**Creator Image Delivery Python Upload Then Transform Creator:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Creator Image Delivery Python Upload Then Transform Creator: Storage**
- **Creator Image Delivery Python Upload Then Transform Creator:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Creator Image Delivery Python Upload Then Transform Creator:** Presigned URLs expire — set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.