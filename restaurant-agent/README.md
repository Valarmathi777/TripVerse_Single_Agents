# 🍽 Agentic AI Restaurant Recommendation System

An intelligent, modular **Agentic AI Restaurant Recommendation Agent** built using **FastAPI**, **Google Gemini AI**, and **Google Places API** (with local dataset fallback).

---

## 🤖 System Architecture & Agent Workflow

```
                User
                  │
                  ▼
     "Find vegetarian food in Tokyo"
                  │
                  ▼
       Preference Parser Agent
                  │
                  ▼
      Restaurant Recommender Agent
                  │
                  ▼
      Google Places API / Dataset
                  │
                  ▼
          Ranking Agent
                  │
                  ▼
        Gemini Explanation Agent
                  │
                  ▼
      Final Restaurant Suggestions
```

### Module Overview

- `app.py`: FastAPI entry point initializing server & CORS middleware.
- `restaurant_agent.py`: High-level entry point orchestrating all sub-agents.
- `prompts.py`: Gemini prompt templates (`RESTAURANT_AGENT_PROMPT`, `PREFERENCE_PARSER_PROMPT`, `EXPLANATION_PROMPT`).
- `config.py`: Environment configuration loading `GEMINI_API_KEY` and `GOOGLE_PLACES_API_KEY`.
- `utils.py`: Helper utilities for rating sorting, deduplication, Haversine distance, budget normalization, and string formatting.
- `agents/`:
  - `preference_parser.py`: Parses unstructured text ("I need cheap vegetarian food in Tokyo") into structured `UserPreference` objects.
  - `restaurant_recommender.py`: Queries Places API or local dataset to retrieve candidate places.
  - `ranking_agent.py`: Filters and ranks candidates based on match score and rating.
  - `explanation_agent.py`: Uses Gemini AI to construct structured, formatted recommendations categorized into **Morning**, **Lunch**, and **Dinner**.
- `services/`:
  - `gemini_service.py`: Google Gemini API integration using `google-genai`.
  - `google_places_service.py`: Google Places API search service.
  - `restaurant_service.py`: Pipeline orchestrator service.
- `models/`:
  - `restaurant.py`: Pydantic schema models (`UserPreference`, `Restaurant`, `RecommendationRequest`, `RecommendationResponse`).
- `data/`:
  - `restaurants.json`: Rich dataset with entries across locations, cuisines, budgets, dietary types, and meal times.
- `api/`:
  - `routes.py`: REST API routes (`POST /api/recommend`, `GET /api/health`, `GET /api/restaurants`).
- `tests/`:
  - `test_restaurant_agent.py`: Pytest suite covering all agents and API endpoints.

---

## 🚀 Setup & Running Locally

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys in `.env`

```env
GEMINI_API_KEY=your_gemini_api_key_here
GOOGLE_PLACES_API_KEY=your_places_api_key_here (optional)
```

> **Note**: If `GOOGLE_PLACES_API_KEY` is omitted, the agent seamlessly uses the local dataset in `data/restaurants.json`.

### 3. Run FastAPI Server

```bash
uvicorn app:app --reload --port 8000
```

Access Interactive API Documentation at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📌 API Endpoints

### `POST /api/recommend`

#### Request (Natural Language)
```json
{
  "query": "I need cheap vegetarian food in Tokyo"
}
```

#### Request (Structured Preferences)
```json
{
  "preferences": {
    "location": "Tokyo",
    "cuisine": "Japanese",
    "budget": "Medium",
    "food_preference": "Vegetarian",
    "min_rating": 4.5
  }
}
```

#### Response Example
```json
{
  "status": "success",
  "preferences": {
    "location": "Tokyo",
    "cuisine": "Japanese",
    "budget": "Low",
    "food_preference": "Vegetarian",
    "min_rating": 4.0,
    "meal_time": null,
    "query": "I need cheap vegetarian food in Tokyo"
  },
  "recommendations": [
    {
      "name": "Cheap Veggie Noodle",
      "location": "Tokyo",
      "cuisine": "Japanese",
      "budget": "Low",
      "type": "Vegetarian",
      "rating": 4.6,
      "address": "Asakusa, Tokyo",
      "meal_time": "Lunch",
      "description": null,
      "reasons": [
        "Offers authentic Vegetarian options",
        "Fits your Low budget preference",
        "Highly rated by diners with ⭐ 4.6 rating"
      ]
    }
  ],
  "formatted_output": "🍽 Restaurant Recommendations\n\n☕ Morning\n• Blue Bottle Coffee ⭐ 4.7\n  Reason:\n  • Offers authentic Vegetarian options\n  • Fits your Low budget preference\n  • Highly rated by diners with ⭐ 4.7 rating\n\n🍣 Lunch\n• Cheap Veggie Noodle ⭐ 4.6\n  Reason:\n  • Offers authentic Vegetarian options\n  • Fits your Low budget preference\n  • Highly rated by diners with ⭐ 4.6 rating"
}
```

---

## 🧪 Running Unit Tests

Execute pytest from project root:

```bash
pytest tests/
```
