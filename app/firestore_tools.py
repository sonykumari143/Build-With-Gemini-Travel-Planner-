"""Firestore database tools for reading and writing travel destinations."""

import json
import google.auth
from google.cloud import firestore

# IMPORTANT: Hardcode Project ID as string (do NOT read from google.auth.default() or GOOGLE_CLOUD_PROJECT)
PROJECT_ID = "qwiklabs-gcp-02-f1b389879af2"


def _get_firestore_client() -> firestore.Client:
    """Return a Firestore client initialized with the hardcoded project ID."""
    creds, _ = google.auth.default()
    return firestore.Client(project=PROJECT_ID, credentials=creds)


def get_destination_from_db(destination_id: str) -> str:
    """Fetch details for a specific destination from the Firestore database.

    Args:
        destination_id: Unique identifier for the destination (e.g. 'tokyo', 'kyoto', 'paris', 'new-york', 'london').

    Returns:
        JSON string containing the destination details or an error message if not found.
    """
    try:
        db = _get_firestore_client()
        doc_id = destination_id.lower().strip().replace(" ", "-")
        doc_ref = db.collection("destinations").document(doc_id)
        doc = doc_ref.get()

        if doc.exists:
            return json.dumps(doc.to_dict(), indent=2)
        else:
            return f"Destination '{destination_id}' not found in database. Try searching or adding it."
    except Exception as e:
        return f"Error reading from Firestore: {str(e)}"


def list_destinations_from_db(country: str = "") -> str:
    """List or search destinations in the Firestore database.

    Args:
        country: Optional country name to filter by (e.g. 'Japan', 'France', 'United States').

    Returns:
        JSON array string of matching destination records.
    """
    try:
        db = _get_firestore_client()
        query = db.collection("destinations")

        if country.strip():
            query = query.where("country", "==", country.strip().title())

        docs = query.stream()
        results = [doc.to_dict() for doc in docs]

        if not results:
            return f"No destinations found in database for query (country='{country}')."

        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error querying Firestore: {str(e)}"


def save_destination_to_db(
    destination_id: str,
    name: str,
    country: str,
    highlights: list[str],
    best_season: str,
    culture_tips: str,
    image_url: str = "",
) -> str:
    """Save or update a travel destination record in the Firestore database.

    Args:
        destination_id: Unique ID key for the destination (e.g., 'sydney', 'rome').
        name: Full city or destination name (e.g., 'Sydney', 'Rome').
        country: Country where destination is located (e.g., 'Australia', 'Italy').
        highlights: List of key attractions or highlights.
        best_season: Best season or months to visit.
        culture_tips: Helpful travel or cultural tips for visitors.
        image_url: Public image URL for destination visual illustration.

    Returns:
        Confirmation message.
    """
    try:
        db = _get_firestore_client()
        doc_id = destination_id.lower().strip().replace(" ", "-")

        data = {
            "id": doc_id,
            "name": name.title(),
            "country": country.title(),
            "highlights": highlights,
            "best_season": best_season,
            "culture_tips": culture_tips,
            "image_url": image_url,
        }

        db.collection("destinations").document(doc_id).set(data)
        return f"Successfully saved destination '{name}' (ID: {doc_id}) to Firestore."
    except Exception as e:
        return f"Error saving to Firestore: {str(e)}"
