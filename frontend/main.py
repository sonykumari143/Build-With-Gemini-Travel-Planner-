"""Minimal FastAPI proxy for a deployed A2A agent (Agent Runtime, agents-cli 1.1.0+).

The browser talks ONLY to this proxy (same origin, no CORS, no GCP creds in the
browser). The proxy authenticates with Application Default Credentials and
forwards chat to the deployed agent over the A2A protocol, returning replies as
structured parts the chat UI knows how to show:

  * {"kind": "text", "text": ...}  -> a normal chat bubble
  * {"kind": "a2ui", "data": ...}  -> one A2UI message (beginRendering /
    surfaceUpdate); static/index.html renders these as a card.
"""

import json
import os
import re
import uuid

import google.auth
import google.auth.transport.requests
import httpx
from a2a.client import ClientConfig, ClientFactory
from a2a.types import (
    AgentCard,
    FilePart,
    Message,
    Part,
    Role,
    TaskArtifactUpdateEvent,
    TextPart,
    TransportProtocol,
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

RESOURCE = os.environ["AGENT_ENGINE_RESOURCE_NAME"]
# The agent's app directory (matches agent_directory in agents-cli-manifest.yaml).
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
# Location is embedded in the resource name: projects/<p>/locations/<loc>/reasoningEngines/<id>.
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]

# A2A endpoint for an Agent Runtime deployment, via the Agent Engine HTTP
# passthrough. The card lives at the well-known path under this base.
A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"

# The agent tags its A2UI data parts with this mime type.
_A2UI_MIME = "application/json+a2ui"

# One set of ADC credentials, refreshed per request (access tokens expire ~1h).
_creds, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)


def _auth_headers() -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {_creds.token}",
        "Content-Type": "application/json",
    }


app = FastAPI()


@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )


# Reuse ONE A2A context per user so the agent remembers the conversation.
_contexts: dict[str, str] = {}
# Cache the agent card after the first fetch.
_card: AgentCard | None = None


async def _get_card(client: httpx.AsyncClient) -> AgentCard:
    global _card
    if _card is None:
        resp = await client.get(A2A_CARD_URL)
        resp.raise_for_status()
        card = AgentCard(**resp.json())
        # Agent Runtime does not serve a public card URL, so point the client at
        # the passthrough base for message sends.
        card.url = A2A_BASE
        _card = card
    return _card


def _clean_text(txt: str) -> str:
    """Strip raw JSON blocks, code fences, and <a2ui-json> tags from text."""
    txt = re.sub(r'<a2ui-json>[\s\S]*?</a2ui-json>', '', txt)
    txt = re.sub(r'```json[\s\S]*?```', '', txt)
    txt = re.sub(r'```[\s\S]*?```', '', txt)
    lines = []
    for line in txt.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith('{') or s.startswith('[') or s.startswith('"') or s.startswith('}') or s.startswith(']'):
            continue
        if s.endswith('}') or s.endswith(']') or s.endswith('},') or s.endswith('],') or s.endswith('{') or s.endswith('['):
            continue
        if ':' in s and ('"id"' in s or '"component"' in s or '"text"' in s or '"usageHint"' in s or '"literalString"' in s or '"explicitList"' in s or '"children"' in s):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _extract_parts(parts: list) -> list[dict]:
    """Turn A2A response parts into structured parts for the chat UI."""
    out: list[dict] = []
    for p in parts:
        root = getattr(p, "root", p)
        if isinstance(root, TextPart) and getattr(root, "text", None):
            txt = root.text

            # 1. Parse <a2ui-json> blocks
            if "<a2ui-json>" in txt:
                try:
                    raw_json = txt.split("<a2ui-json>")[1].split("</a2ui-json>")[0].strip()
                    data = json.loads(raw_json)
                    prefix = txt.split("<a2ui-json>")[0].strip()
                    suffix = txt.split("</a2ui-json>")[-1].strip()
                    clean_prose = _clean_text(prefix + "\n" + suffix)
                    if clean_prose:
                        out.append({"kind": "text", "text": clean_prose})
                    if isinstance(data, list):
                        for item in data:
                            out.append({"kind": "a2ui", "data": item})
                    else:
                        out.append({"kind": "a2ui", "data": data})
                    continue
                except Exception:
                    pass

            # 2. Parse markdown code fences with json ```json ... ```
            if "```json" in txt or "```" in txt:
                try:
                    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', txt)
                    if match:
                        raw_json = match.group(1).strip()
                        data = json.loads(raw_json)
                        if isinstance(data, (dict, list)):
                            clean_prose = re.sub(r'```(?:json)?[\s\S]*?```', '', txt).strip()
                            clean_prose = _clean_text(clean_prose)
                            if clean_prose:
                                out.append({"kind": "text", "text": clean_prose})
                            if isinstance(data, list):
                                for item in data:
                                    out.append({"kind": "a2ui", "data": item})
                            else:
                                out.append({"kind": "a2ui", "data": data})
                            continue
                except Exception:
                    pass

            # 3. Check if text is raw JSON object/array
            trimmed = txt.strip()
            if (trimmed.startswith('{') and trimmed.endswith('}')) or (trimmed.startswith('[') and trimmed.endswith(']')):
                try:
                    data = json.loads(trimmed)
                    if isinstance(data, (dict, list)):
                        if isinstance(data, list):
                            for item in data:
                                out.append({"kind": "a2ui", "data": item})
                        else:
                            out.append({"kind": "a2ui", "data": data})
                        continue
                except Exception:
                    pass

            clean_txt = _clean_text(txt)
            if clean_txt:
                out.append({"kind": "text", "text": clean_txt})
        elif getattr(root, "data", None) is not None:
            meta = getattr(root, "metadata", None) or {}
            mime = meta.get("mimeType") if isinstance(meta, dict) else None
            if mime == _A2UI_MIME:
                out.append({"kind": "a2ui", "data": root.data})
        elif isinstance(root, FilePart):
            uri = getattr(getattr(root, "file", None), "uri", None)
            if uri:
                out.append({"kind": "text", "text": uri})
    return out


@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"

    print(f"[{user_id}] Incoming message: {message[:100]}")

    async def _send_to_agent(client: httpx.AsyncClient, ctx_id: str | None) -> tuple[list[dict], str | None]:
        card = await _get_card(client)
        factory = ClientFactory(
            ClientConfig(
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json,
                ],
                httpx_client=client,
            )
        )
        a2a_client = factory.create(card)

        msg = Message(
            message_id=str(uuid.uuid4()),
            role=Role.user,
            parts=[Part(root=TextPart(text=message))],
            context_id=ctx_id,
        )

        out_parts: list[dict] = []
        last_task = None
        new_ctx = ctx_id
        got_artifact_update = False

        async for event in a2a_client.send_message(msg):
            if not isinstance(event, tuple):
                continue
            task, update = event
            if task is not None:
                last_task = task
                if getattr(task, "context_id", None):
                    new_ctx = task.context_id
            if isinstance(update, TaskArtifactUpdateEvent):
                got_artifact_update = True
                out_parts.extend(_extract_parts(update.artifact.parts))

        if not got_artifact_update and last_task is not None:
            for artifact in getattr(last_task, "artifacts", None) or []:
                out_parts.extend(_extract_parts(artifact.parts))
            if not out_parts and getattr(last_task, "history", None):
                for m in reversed(last_task.history):
                    if getattr(m, "role", None) in (Role.agent, "agent"):
                        extracted = _extract_parts(m.parts)
                        if extracted:
                            out_parts = extracted + out_parts

        return out_parts, new_ctx

    parts: list[dict] = []
    async with httpx.AsyncClient(headers=_auth_headers(), timeout=120) as client:
        current_ctx = _contexts.get(user_id)
        try:
            parts, new_ctx = await _send_to_agent(client, current_ctx)
            if new_ctx:
                _contexts[user_id] = new_ctx
        except Exception as err:
            print(f"[{user_id}] Context error with {current_ctx}: {err}. Retrying fresh...")
            _contexts.pop(user_id, None)
            try:
                parts, new_ctx = await _send_to_agent(client, None)
                if new_ctx:
                    _contexts[user_id] = new_ctx
            except Exception as retry_err:
                print(f"[{user_id}] Retry failed: {retry_err}")
                parts = [{"kind": "text", "text": f"Error communicating with agent: {retry_err}"}]

        if not parts and current_ctx:
            print(f"[{user_id}] Empty parts with context {current_ctx}. Retrying fresh...")
            _contexts.pop(user_id, None)
            try:
                parts, new_ctx = await _send_to_agent(client, None)
                if new_ctx:
                    _contexts[user_id] = new_ctx
            except Exception as retry_err:
                print(f"[{user_id}] Retry failed: {retry_err}")

    if not parts:
        parts = [{"kind": "text", "text": "Hello! How can I help you with your travel plans today?"}]

    print(f"[{user_id}] Returning {len(parts)} parts")
    return JSONResponse({"parts": parts})


STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
# Serve the chat UI (keep this mount last so /chat wins).
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
