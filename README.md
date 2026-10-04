# ✈️ Travel Planner AI

An intelligent AI Travel Concierge and Itinerary Assistant powered by the **Google Agent Development Kit (ADK)**, **Gemini Models**, **Vertex AI Memory Bank**, **Google Cloud Storage**, **Firestore**, and interactive **A2UI** component cards.

![Travel Planner AI Demo](./demo.gif)

---

## 🌟 Capabilities & Features

Travel Planner AI helps travelers discover destinations, generate custom multi-day itineraries, visualize landmarks, look up local weather and nearby places, and manage travel preferences.

### 🧠 Persistent Traveler Memory
- **Vertex AI Memory Bank**: Integrates `VertexAiMemoryBankService` to automatically remember user preferences, dietary needs, family members, budget styles, and past travel destinations across conversations.

### 🗺️ Location & Discovery Services
- **Google Maps Places API (New)**: Finds nearby restaurants, hotels, and attractions around specific landmarks (`find_nearby_places`).
- **Google Maps Geocoding API**: Converts street addresses and landmark names into precise latitude and longitude coordinates (`geocode_address`).
- **Destination Database (Firestore)**: Reads and persists curated destination guides, travel tips, and saved itineraries in Google Cloud Firestore (`get_destination_from_db`, `list_destinations_from_db`, `save_destination_to_db`).

### 🎨 Visual & Media Generation
- **Gemini Image Generation**: Generates scenic landmark illustrations and destination visuals using `gemini-3.1-flash-lite-image` (`generate_destination_image`).
- **Gemini Omni Video Generation**: Generates short 3-second travel landmark videos using `gemini-omni-flash-preview` in the `global` region (`generate_destination_video`).
- **Cloud Storage & Playground Artifacts**: Uploads generated images and videos directly to a public Google Cloud Storage bucket and registers session artifacts with `tool_context.save_artifact` for inspection in the Playground's Artifacts panel.

### 🌦️ Live Travel Utilities
- **Destination Weather**: Fetches real-time weather forecasts and temperature trends (`get_destination_weather`).
- **Currency Exchange Rates**: Calculates live exchange rates for international trip budgeting (`get_currency_exchange_rates`).
- **Public Holidays**: Checks upcoming public holidays at destinations (`get_destination_public_holidays`).
- **Day-by-Day Itinerary Planner**: Generates tailored multi-day travel schedules with morning, afternoon, and evening recommendations (`generate_itinerary`).
- **Python Sandbox Execution**: Executes Python code in a secure ADK sandbox for budget calculations and expense splitting.

### 📱 Interactive A2UI Frontend
- **Structured A2UI Cards & Map Embeds**: Renders structured visual cards, daily itinerary schedules, and embedded interactive Google Maps alongside clean human-readable Markdown text.
- **Glassmorphic Responsive Web App**: FastAPI web application with dark/light mode toggle, dynamic quick-prompt chips, 1-click copy button, and an image lightbox viewer.

---

## 🏗️ Project Architecture

```
travel-planner/
├── app/                       # Core Agent Code (ADK)
│   ├── agent.py               # Main Root Agent configuration & callbacks
│   ├── a2ui_utils.py          # A2UI response formatting & filtering
│   ├── api_tools.py           # Weather, Currency, & Holiday APIs
│   ├── firestore_tools.py     # Firestore database lookup & persistence
│   ├── gcs_tools.py           # Cloud Storage upload helper
│   ├── image_gen_tools.py     # Gemini image generation tool
│   ├── video_gen_tools.py     # Gemini Omni video generation tool
│   ├── maps_tools.py          # Google Maps Places & Geocoding tools
│   ├── travel_tools.py        # Itinerary generator & guide tools
│   └── fast_api_app.py        # FastAPI server endpoint
├── frontend/                  # Web Frontend
│   ├── main.py                # Frontend FastAPI app server
│   └── static/index.html      # Responsive UI template with glassmorphic theme
├── demo.gif                   # Looping preview animation
├── agents-cli-manifest.yaml   # Agents CLI configuration
└── pyproject.toml             # Python dependencies
```

---

## 🚀 Setup & Local Execution

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) or standard `pip`
- Google Cloud Project with Vertex AI, Firestore, Cloud Storage, and Google Maps APIs enabled.

### 1. Install Dependencies
```bash
uv sync
# Or using standard pip
pip install -r pyproject.toml
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and set your GCP configuration:
```bash
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_MAPS_API_KEY="your-google-maps-api-key"
```

### 3. Run Agent in Development Playground
To launch the interactive ADK agent playground locally:
```bash
agents-cli playground
```

### 4. Run Web Application Locally
To start the FastAPI web server locally:
```bash
uv run uvicorn frontend.main:app --host 0.0.0.0 --port 8080
```

---

## ☁️ Deployment

Deploy the agent to **Agent Engine / Agent Runtime**:
```bash
gcloud config set project your-gcp-project-id
agents-cli deploy --project your-gcp-project-id --region us-east1
```

Deploy the frontend web app to **Cloud Run**:
```bash
gcloud run deploy travel-planner-frontend \
  --source . \
  --region us-east1 \
  --allow-unauthenticated
```
