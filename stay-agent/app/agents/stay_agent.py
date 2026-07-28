import json

from app.services.gemini_service import generate_response
from app.prompts.stay_prompt import STAY_PROMPT
from app.services.database import save_stay

def generate_stay(
    destination,
    checkin,
    checkout,
    guests,
    budget,
    travel_style,
    accommodation,
    requirements,
):

    prompt = f"""
{STAY_PROMPT}

Destination:
{destination}

Check-in:
{checkin}

Check-out:
{checkout}

Guests:
{guests}

Budget:
{budget}

Travel Style:
{travel_style}

Accommodation:
{accommodation}

Requirements:
{requirements}
"""

    response = generate_response(prompt)

    # Compile the request details for saving
    request_data = {
        "destination": destination,
        "checkin": checkin,
        "checkout": checkout,
        "guests": guests,
        "budget": budget,
        "travel_style": travel_style,
        "accommodation": accommodation,
        "requirements": requirements
    }

    try:
        parsed_response = json.loads(response)
    except Exception as e:
        print(f"Failed to parse response as JSON: {e}")
        # In case of bad parsing, build a standard fallback structure
        parsed_response = {
            "recommended_area": "Main Area",
            "area_reason": "Encountered formatting issues when parsing the AI response.",
            "hotels": [
                {
                    "name": "Standard Local Hotel",
                    "price_per_night": budget,
                    "rating": "4.0",
                    "reason": "AI response could not be fully parsed, fallback layout generated.",
                    "nearby_places": [destination],
                    "nearest_transport": "Main Station",
                    "pros": ["Central location"],
                    "cons": ["Basic service"]
                }
            ],
            "estimated_total_cost": budget,
            "best_choice": "Standard Local Hotel",
            "travel_tips": ["Consult travel guides for local information."]
        }

    # Merge input request details into the returned response to align with database schemas
    for k, v in request_data.items():
        parsed_response[k] = v

    try:
        stay_id = save_stay(request_data, parsed_response)
        parsed_response["id"] = stay_id
        parsed_response["notes"] = ""
        parsed_response["rating"] = 0
        parsed_response["is_bookmarked"] = 0
    except Exception as e:
        print(f"Failed to save stay plan to the database: {e}")
        parsed_response["id"] = None
        parsed_response["notes"] = ""
        parsed_response["rating"] = 0
        parsed_response["is_bookmarked"] = 0

    return parsed_response