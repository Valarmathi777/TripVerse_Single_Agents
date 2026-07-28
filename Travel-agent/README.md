# Move Agent — Smart Travel Planner

AI-powered route intelligence that scores every transport option across 8 modes using real-time weather, traffic, and your personal preferences.

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://localhost:8000

## API Keys (optional but recommended)

Set these as environment variables for live data:

| Variable | Service | Free Tier |
|---|---|---|
| `OPENWEATHER_API_KEY` | OpenWeatherMap | ✅ |
| `OPENROUTE_API_KEY` | OpenRouteService | ✅ |
| `GEOAPIFY_API_KEY` | Geoapify | ✅ |

Without keys the app still works using estimated calculations.

## API Usage

```bash
POST /api/plan
Content-Type: application/json

{
  "source": "Tokyo",
  "destination": "Mount Fuji",
  "date": "2026-08-15",
  "time": "08:30",
  "budget": 3000,
  "group_size": 2,
  "preference": "fastest"
}
```

Preferences: `fastest` · `cheapest` · `comfort` · `eco` · `scenic`

## Project Structure

```
move-agent/
├── app.py              # FastAPI entry point
├── config.py           # API keys & weights
├── api/
│   ├── routing.py      # /api/plan endpoint
│   ├── transport.py    # Multi-mode transport fetcher
│   ├── weather.py      # OpenWeatherMap integration
│   └── traffic.py      # Traffic level estimator
├── planner/
│   ├── route_finder.py # Filter invalid options
│   ├── scorer.py       # Weighted AI scoring
│   └── optimizer.py    # Rank & explain best route
├── models/schemas.py   # Pydantic models
├── utils/helpers.py    # Geocoding & time utils
├── templates/index.html
└── static/
    ├── css/style.css
    └── js/main.js
```
