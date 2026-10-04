"""Travel tools for the Travel Planner Agent."""

import datetime
import json
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo


def get_destination_guide(destination: str) -> str:
    """Retrieves top attractions, local dining, culture, and travel tips for a destination.

    Args:
        destination: The city or region to get a guide for (e.g., 'Tokyo', 'Paris', 'New York').

    Returns:
        A detailed summary of top highlights, food recommendations, and travel tips.
    """
    dest_lower = destination.lower().strip()
    
    guides = {
        "tokyo": {
            "highlights": ["Senso-ji Temple", "Shibuya Crossing", "Meiji Shrine", "Akihabara", "Shinjuku Gyoen"],
            "food": ["Ramen at Ichiran", "Tsukiji Outer Market Sushi", "Yakitori in Omoide Yokocho", "Matcha Sweets"],
            "tips": "Suica/Pasmo card recommended for public transit. Tipping is not expected.",
            "best_season": "Spring (Cherry Blossoms) or Autumn (Crisp air & foliage)"
        },
        "kyoto": {
            "highlights": ["Fushimi Inari Shrine", "Arashiyama Bamboo Grove", "Kinkaku-ji (Golden Pavilion)", "Gion District"],
            "food": ["Kaiseki dining", "Yudofu (tofu hot pot)", "Uji Matcha teas"],
            "tips": "Early morning visits avoid crowds at Fushimi Inari and Arashiyama.",
            "best_season": "October-November & April-May"
        },
        "paris": {
            "highlights": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral", "Montmartre", "Musée d'Orsay"],
            "food": ["Fresh Croissants & Baguettes", "Duck Confit", "Macarons from Ladurée", "French Cheese & Wine"],
            "tips": "Purchase museum passes in advance to skip line queues.",
            "best_season": "May-June or September-October"
        },
        "new york": {
            "highlights": ["Central Park", "Statue of Liberty", "Empire State Building", "Broadway", "The Met"],
            "food": ["NY Style Pizza", "Bagels with Lox", "Pastrami at Katz Delicatessen", "Food trucks"],
            "tips": "Use the NYC Subway with contactless OMNY payments.",
            "best_season": "Autumn (September-November) or Spring"
        }
    }
    
    for key, data in guides.items():
        if key in dest_lower:
            return (
                f"🌟 Travel Guide for {destination.title()}:\n"
                f"• Top Highlights: {', '.join(data['highlights'])}\n"
                f"• Culinary Recommendations: {', '.join(data['food'])}\n"
                f"• Best Time to Visit: {data['best_season']}\n"
                f"• Insider Tip: {data['tips']}"
            )
            
    return (
        f"🌟 Travel Guide for {destination.title()}:\n"
        f"• Top Highlights: Historic Old Town, Scenic Viewpoints, Cultural Landmarks, Central Market\n"
        f"• Culinary Recommendations: Local specialties, artisanal cafes, and street food markets\n"
        f"• Best Time to Visit: Spring and Autumn for pleasant weather\n"
        f"• Insider Tip: Explore on foot or use local public transit for an authentic experience."
    )


def generate_itinerary(destination: str, days: int = 3, style: str = "balanced") -> str:
    """Generates a day-by-day travel itinerary with morning, afternoon, and evening activities.

    Args:
        destination: The destination city or area.
        days: Number of days for the trip (e.g. 1 to 7).
        style: Travel preference (e.g., 'foodie', 'culture', 'adventure', 'budget', 'relaxed', 'balanced').

    Returns:
        A structured day-by-day travel itinerary.
    """
    days = max(1, min(days, 7))
    style_label = style.title()
    dest_name = destination.title()
    
    itinerary = [f"✈️ {days}-Day '{style_label}' Itinerary for {dest_name}:"]
    
    sample_activities = [
        ("Morning: Neighborhood walking tour & local breakfast", "Afternoon: Visit iconic museum/landmark", "Evening: Sunset viewpoint & traditional dinner"),
        ("Morning: Historical temple or monument exploration", "Afternoon: Artisan market & local shopping", "Evening: Cultural performance or night market"),
        ("Morning: Scenic garden or nature park stroll", "Afternoon: Local cooking class or food tasting", "Evening: Rooftop lounge or riverside dining"),
        ("Morning: Architectural landmarks tour", "Afternoon: Waterfront boat cruise or bike ride", "Evening: Speakeasy bar or local theater show"),
        ("Morning: Day trip to nearby scenic village/coastal spot", "Afternoon: Traditional workshop or gallery visit", "Evening: Farewell tasting menu dinner")
    ]
    
    for day in range(1, days + 1):
        idx = (day - 1) % len(sample_activities)
        morning, afternoon, evening = sample_activities[idx]
        itinerary.append(
            f"📅 Day {day}:\n"
            f"  • {morning}\n"
            f"  • {afternoon}\n"
            f"  • {evening}"
        )
        
    return "\n\n".join(itinerary)


def illustrate_destination(destination: str, landmark: str = "") -> str:
    """Generates a visual illustration description and public image URL for a destination or landmark.

    Args:
        destination: The name of the destination (e.g., 'Tokyo', 'Paris').
        landmark: Optional specific landmark or scenery to illustrate (e.g., 'Eiffel Tower at sunset', 'Fushimi Inari torii gates').

    Returns:
        A visual description and destination image link.
    """
    target = f"{landmark}, {destination}" if landmark else destination
    dest_lower = destination.lower()
    
    sample_images = {
        "tokyo": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?q=80&w=1000&auto=format&fit=crop",
        "kyoto": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?q=80&w=1000&auto=format&fit=crop",
        "paris": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?q=80&w=1000&auto=format&fit=crop",
        "new york": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?q=80&w=1000&auto=format&fit=crop",
        "london": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?q=80&w=1000&auto=format&fit=crop",
        "rome": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?q=80&w=1000&auto=format&fit=crop",
    }
    
    img_url = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?q=80&w=1000&auto=format&fit=crop"
    for k, v in sample_images.items():
        if k in dest_lower:
            img_url = v
            break
            
    return (
        f"🎨 Visual Illustration for {target}:\n"
        f"Description: A vibrant, atmospheric view capturing the unique charm, architecture, and lighting of {target}.\n"
        f"Image URL: {img_url}"
    )


def get_destination_weather(destination: str) -> str:
    """Fetches real-time weather and temperature for a destination using Open-Meteo API.

    Args:
        destination: City or destination name (e.g. 'Tokyo', 'Paris', 'New York').

    Returns:
        String with current temperature, wind speed, and live conditions.
    """
    try:
        encoded_city = urllib.parse.quote(destination.strip())
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1&language=en&format=json"
        
        req = urllib.request.Request(geo_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            geo_data = json.loads(resp.read().decode())
            
        if not geo_data.get("results"):
            return f"Unable to find weather location for '{destination}'."
            
        loc = geo_data["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        city_name = loc.get("name", destination.title())
        country = loc.get("country", "")
        
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
        req_w = urllib.request.Request(weather_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_w, timeout=5) as resp_w:
            w_data = json.loads(resp_w.read().decode())
            
        current = w_data.get("current_weather", {})
        temp_c = current.get("temperature", "N/A")
        temp_f = round(temp_c * 9/5 + 32, 1) if isinstance(temp_c, (int, float)) else "N/A"
        wind_speed = current.get("windspeed", "N/A")
        
        return (
            f"🌤️ Real-Time Weather for {city_name}, {country}:\n"
            f"• Current Temperature: {temp_c}°C ({temp_f}°F)\n"
            f"• Wind Speed: {wind_speed} km/h\n"
            f"• Status: Live weather fetched via Open-Meteo."
        )
    except Exception as e:
        return f"Unable to fetch live weather for '{destination}': {str(e)}"
