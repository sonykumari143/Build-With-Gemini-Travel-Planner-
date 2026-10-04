"""Gemini Omni Video Generation tools for travel planner destinations."""

import base64
import re
import google.auth
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcoded bucket and project ID
BUCKET_NAME = "travel-planner-media-f1b38987"
PROJECT_ID = "qwiklabs-gcp-02-f1b389879af2"


def generate_destination_video(prompt: str, filename: str, tool_context: ToolContext) -> str:
    """Generate a short video for a travel destination or landmark using the gemini-omni-flash-preview model in the global region.

    Generates video bytes, saves the video as a session artifact using tool_context.save_artifact
    for the Playground, uploads the video bytes directly to public Cloud Storage, and returns its public HTTPS URL.

    Args:
        prompt: Descriptive text prompt for the video (e.g., 'A 3-second aerial shot of Mt. Fuji at sunset').
        filename: Destination video filename to save (e.g., 'mt_fuji_sunset.mp4').
        tool_context: ToolContext provided automatically by the ADK framework.

    Returns:
        The public HTTPS URL of the uploaded video in Cloud Storage (https://storage.googleapis.com/<bucket>/<object>).
    """
    try:
        # Sanitize filename
        clean_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename.strip().lower())
        if not clean_filename.endswith(".mp4"):
            clean_filename += ".mp4"

        # 1. Generate video bytes using gemini-omni-flash-preview in global region
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        video_content = getattr(interaction, "output_video", None)
        if not video_content or not getattr(video_content, "data", None):
            return f"Error: No video output generated for prompt '{prompt}'."

        raw_data = video_content.data
        if isinstance(raw_data, str):
            video_bytes = base64.b64decode(raw_data)
        elif isinstance(raw_data, bytes):
            video_bytes = raw_data
        else:
            return f"Error: Unexpected video data type '{type(raw_data)}'."

        mime_type = getattr(video_content, "mime_type", "video/mp4") or "video/mp4"

        # 2. Save video with tool_context.save_artifact so it shows up in Playground Artifacts
        if tool_context is not None:
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=clean_filename, artifact=artifact_part)

        # 3. Upload video bytes to public Cloud Storage bucket without writing to local file
        creds, _ = google.auth.default()
        storage_client = storage.Client(project=PROJECT_ID, credentials=creds)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(clean_filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{clean_filename}"
        return f"Successfully generated destination video! Public URL: {public_url}"
    except Exception as e:
        return f"Error generating destination video: {str(e)}"
