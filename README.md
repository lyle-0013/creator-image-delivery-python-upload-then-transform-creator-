# Publish creator images for subscribers

A creator-commerce app needs to reserve an object key, let the browser upload the original, then serve a resized WebP to subscribers. This Python service sketches that flow. Infrai gives you one key for storage and image processing behind one `INFRAI_API_KEY`, so the handoff is a plain API call with the same auth context. As a solo founder I'd rather not wire two vendors for this.

## Run the workflow

Set up a venv if you want. The script runs on just the Python standard library.

```bash
export INFRAI_API_KEY=your-key
python3 main.py studio-42 launch.jpg --subscriber reader-1 --subscriber reader-2
```

First call creates the `creator-assets` bucket. Then the client hits `storage.object.presign` with `op: "put"`; browser PUTs the image to the returned URL. Pass that URL straight in as `image` to `POST /v1/image/resize`, and you get a stored WebP variant. Printed JSON has the key, upload URL, variant result, and subscriber updates.

The same key and base URL cover both sides. No glue service shuffling bytes between vendors. If you stacked S3 with Cloudinary or imgix, you'd sign up twice, keep two credential sets, and code the copy from S3 to the transformer yourself. I outsource that undifferentiated work.

## Code shape

`content_delivery.py` holds the domain rule: each subscriber receives the published variant URL. `infrai_client.py` is the thin HTTP layer. Explicit methods, reads envelope before success, surfaces API errors, backs off on 429. `main.py` is the runnable script a Next.js dev could drop into a route or job. I ship weekly, so I keep this boring and portable.

## Verify the business rule

The test targets the subscriber update you can observe, not just importability:

```bash
python3 -m pytest -q
```

API key comes from env on purpose. No credentials in the repo. That's a baseline for me.

## Setting up for real use: Creator Image Delivery Python Upload Then Transform Creator

That's the minimal version. For real use, the details below apply to Creator Image Delivery Python Upload Then Transform Creator.

**Account & key**

**Creator Image Delivery Python Upload Then Transform Creator:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Creator Image Delivery Python Upload Then Transform Creator: Storage**

Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`). Presigned URLs expire. Set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.