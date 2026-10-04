"""Seed Firestore database with initial destination records."""

import google.auth
from google.cloud import firestore

# IMPORTANT: Hardcoded Project ID string (do NOT use GOOGLE_CLOUD_PROJECT or google.auth.default project ID)
PROJECT_ID = "qwiklabs-gcp-02-f1b389879af2"

DESTINATIONS = [
    {
        "id": "tokyo",
        "name": "Tokyo",
        "country": "Japan",
        "highlights": ["Senso-ji Temple", "Shibuya Crossing", "Meiji Shrine", "Akihabara", "Shinjuku Gyoen"],
        "best_season": "Spring (Cherry Blossoms) or Autumn",
        "culture_tips": "Get a Suica/Pasmo card for seamless transit. Tipping is not expected.",
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?q=80&w=1000&auto=format&fit=crop"
    },
    {
        "id": "kyoto",
        "name": "Kyoto",
        "country": "Japan",
        "highlights": ["Fushimi Inari Shrine", "Arashiyama Bamboo Grove", "Kinkaku-ji (Golden Pavilion)", "Gion District"],
        "best_season": "October-November & April-May",
        "culture_tips": "Early morning visits avoid crowds at temples. Respect geisha in Gion.",
        "image_url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?q=80&w=1000&auto=format&fit=crop"
    },
    {
        "id": "paris",
        "name": "Paris",
        "country": "France",
        "highlights": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral", "Montmartre", "Musée d'Orsay"],
        "best_season": "May-June or September-October",
        "culture_tips": "Greet shopkeepers with 'Bonjour'. Purchase museum passes in advance.",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?q=80&w=1000&auto=format&fit=crop"
    },
    {
        "id": "new-york",
        "name": "New York",
        "country": "United States",
        "highlights": ["Central Park", "Statue of Liberty", "Empire State Building", "Broadway", "The Met"],
        "best_season": "September-November or Spring",
        "culture_tips": "Use contactless OMNY for NYC Subway. Tipping 18-20% is standard in restaurants.",
        "image_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?q=80&w=1000&auto=format&fit=crop"
    },
    {
        "id": "london",
        "name": "London",
        "country": "United Kingdom",
        "highlights": ["Big Ben & Parliament", "Tower of London", "British Museum", "Hyde Park", "West End"],
        "best_season": "May-September",
        "culture_tips": "Stand on the right on escalators. Tap in/out with contactless payment on Tube.",
        "image_url": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?q=80&w=1000&auto=format&fit=crop"
    }
]


def main():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    creds, _ = google.auth.default()
    db = firestore.Client(project=PROJECT_ID, credentials=creds)
    collection_ref = db.collection("destinations")

    for dest in DESTINATIONS:
        doc_id = dest["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(dest)
        print(f"✓ Seeded destination: {dest['name']} (ID: {doc_id})")

    print("\n🎉 Firestore database successfully seeded!")


if __name__ == "__main__":
    main()
