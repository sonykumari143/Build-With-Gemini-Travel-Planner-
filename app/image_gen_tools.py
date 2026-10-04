"""Gemini Image Generation tools for travel planner destinations."""

import re
import google.auth
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcoded bucket and project ID
BUCKET_NAME = "travel-planner-media-f1b38987"
PROJECT_ID = "qwiklabs-gcp-02-f1b389879af2"


def generate_destination_image(prompt: str, filename: str, tool_context: ToolContext) -> str:
    """Generate an image for a travel destination or landmark using the gemini-3.1-flash-lite-image model.

    Generates image bytes, saves the image as a session artifact using tool_context.save_artifact
    for the Playground, uploads the image bytes to public Cloud Storage, and returns its public HTTPS URL.

    Args:
        prompt: Descriptive text prompt for the image (e.g., 'A vibrant sunset over Fushimi Inari shrine in Kyoto').
        filename: Destination filename to save (e.g., 'kyoto_fushimi_inari.jpg').
        tool_context: ToolContext provided automatically by the ADK framework.

    Returns:
        The public HTTPS URL of the uploaded image in Cloud Storage (https://storage.googleapis.com/<bucket>/<object>).
    """
    try:
        # Sanitize filename
        clean_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename.strip().lower())
        if not (clean_filename.endswith(".jpg") or clean_filename.endswith(".jpeg") or clean_filename.endswith(".png")):
            clean_filename += ".jpg"

        # 1. Generate image bytes using gemini-3.1-flash-lite-image in global region
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt
        )

        image_bytes = None
        mime_type = "image/jpeg"

        if response.candidates:
            for candidate in response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.inline_data and part.inline_data.data:
                            image_bytes = part.inline_data.data
                            if part.inline_data.mime_type:
                                mime_type = part.inline_data.mime_type
                            break

        if not image_bytes:
            return f"Error: No image bytes generated for prompt '{prompt}'."

        # 2. Save image with tool_context.save_artifact so it appears in Playground's Artifacts panel
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=clean_filename, artifact=artifact_part)

        # 3. Upload image bytes directly to Cloud Storage bucket (without writing to local file)
        creds, _ = google.auth.default()
        storage_client = storage.Client(project=PROJECT_ID, credentials=creds)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(clean_filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{clean_filename}"
        return f"Successfully generated destination image! Public URL: {public_url}"
    except Exception as e:
        return f"Error generating destination image: {str(e)}"
