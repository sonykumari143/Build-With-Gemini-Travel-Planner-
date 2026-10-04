"""Cloud Storage tools for uploading and storing destination media."""

import urllib.request
import google.auth
from google.cloud import storage

# Hardcoded bucket and project ID
BUCKET_NAME = "travel-planner-media-f1b38987"
PROJECT_ID = "qwiklabs-gcp-02-f1b389879af2"


def upload_image_to_gcs(image_url: str, filename: str) -> str:
    """Download an image from a URL and upload it to the project's public Cloud Storage bucket.

    Args:
        image_url: Public web URL of the image to download.
        filename: Target filename to save in GCS bucket (e.g. 'tokyo.jpg', 'kyoto.jpg').

    Returns:
        The public HTTPS URL of the uploaded object in Cloud Storage.
    """
    try:
        req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            image_data = resp.read()

        creds, _ = google.auth.default()
        client = storage.Client(project=PROJECT_ID, credentials=creds)
        bucket = client.bucket(BUCKET_NAME)
        clean_filename = filename.strip().lower().replace(" ", "_")
        if not (clean_filename.endswith(".jpg") or clean_filename.endswith(".png")):
            clean_filename += ".jpg"

        blob = bucket.blob(clean_filename)
        blob.upload_from_string(image_data, content_type="image/jpeg")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{clean_filename}"
        return f"Successfully uploaded image to Cloud Storage. Public URL: {public_url}"
    except Exception as e:
        return f"Error uploading image to GCS: {str(e)}"
