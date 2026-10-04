# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from pathlib import Path

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from .a2ui_utils import a2ui_callback
from .api_tools import (
    get_currency_exchange_rates,
    get_destination_public_holidays,
)
from .firestore_tools import (
    get_destination_from_db,
    list_destinations_from_db,
    save_destination_to_db,
)
from .gcs_tools import upload_image_to_gcs
from .image_gen_tools import generate_destination_image
from .video_gen_tools import generate_destination_video
from .maps_tools import (
    find_nearby_places,
    geocode_address,
)
from .travel_tools import (
    generate_itinerary,
    get_destination_guide,
    get_destination_weather,
    illustrate_destination,
)

# Active Memory Bank Instance
PROJECT_ID = "qwiklabs-gcp-02-f1b389879af2"
LOCATION = "us-central1"
MEMORY_BANK_ID = "1563997566150901760"

# Memory Bank Service for app redeployment
memory_service = VertexAiMemoryBankService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=MEMORY_BANK_ID,
)


# Memory extraction callback: sends turn events to Memory Bank after each agent turn
async def generate_memories_callback(callback_context: CallbackContext):
    mem_svc = getattr(callback_context, "memory_service", None)
    if mem_svc is not None:
        try:
            await callback_context.add_session_to_memory()
        except Exception as e:
            print(f"Warning: Memory extraction failed: {e}")
    return None


# Load code executor from deployment_metadata.json if available
code_executor = None
DEPLOYMENT_METADATA_PATH = Path(__file__).resolve().parent.parent / "deployment_metadata.json"

if DEPLOYMENT_METADATA_PATH.exists():
    try:
        with open(DEPLOYMENT_METADATA_PATH, "r") as f:
            metadata = json.load(f)
            sandbox_name = metadata.get("sandbox_resource_name")
            engine_id = metadata.get("remote_agent_runtime_id")

            if sandbox_name:
                code_executor = AgentEngineSandboxCodeExecutor(sandbox_resource_name=sandbox_name)
            elif engine_id:
                code_executor = AgentEngineSandboxCodeExecutor(agent_engine_resource_name=engine_id)
    except Exception as e:
        print(f"Warning: Failed to load sandbox code executor: {e}")

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description="You are an expert AI Travel Concierge and Itinerary Planner.",
    workflow_description=(
        "Analyze the user's travel request. Always remember and personalize itineraries around the user's stated personal facts, "
        "including birthdays, anniversaries, dietary needs, family members, and travel preferences across conversations. "
        "Execute Python code safely in the sandbox when complex calculations or data processing are needed. "
        "Generate custom destination images with Gemini Image model, convert addresses to coordinates with Geocoding, "
        "find nearby places with Places API (New), fetch live weather, public holidays, and currency exchange rates, "
        "query or save destinations in Firestore, upload images to Cloud Storage, generate customized itineraries, and present structured A2UI cards."
    ),
    ui_description=(
        "Always provide a friendly, human-readable prose response in clean text with markdown formatting (headers, bullet points, recommendations, emojis). "
        "Alongside your text response, you may output structured A2UI cards for visual components. "
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, Image, and Map. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms. "
        "When locations, addresses, or places are mentioned, include a Map component "
        'e.g. {"Map": {"query": {"literalString": "Tokyo Tower, Tokyo"}, "latitude": 35.6585, "longitude": 139.7454}}. '
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example from Cloud Storage or returned by illustrate_destination or generate_destination_image). "
        "Set the Image url to that exact https link. Never point an "
        "Image at a bare filename or non-http(s) path."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=code_executor,
    tools=[
        PreloadMemoryTool(),
        get_destination_guide,
        get_destination_weather,
        geocode_address,
        find_nearby_places,
        generate_destination_image,
        generate_destination_video,
        get_destination_public_holidays,
        get_currency_exchange_rates,
        generate_itinerary,
        illustrate_destination,
        get_destination_from_db,
        list_destinations_from_db,
        save_destination_to_db,
        upload_image_to_gcs,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
