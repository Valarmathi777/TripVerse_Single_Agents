# Budget Agent 🧭

An AI-powered travel budget planner for Indian destinations. Enter a destination,
trip length, traveler count, and budget — get a full category-wise cost ledger,
a daily spend chart, and an AI-generated recommendation on how to stay on budget.

```
React Frontend  →  FastAPI Backend  →  Gemini + Geoapify + ORS + Open-Meteo + Frankfurter + CSV datasets
```

## Project structure

```
budget-agent/
├── backend/            FastAPI app, budget engine, ML model, datasets
├── frontend/            React + Vite + Tailwind + Recharts dashboard
├── docker-compose.yml    Postgres + backend + frontend, one command
├── .env                  Your real API keys (never commit this)
└── .env.example          Template showing what keys are needed
```

## 1. API keys — what you need and where to get them

| Key | Required? | Where to get it | Notes |
|---|---|---|---|
| `GEMINI_API_KEY` | Recommended | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) | Powers the AI Recommendation panel. Without it, the app falls back to a clear rule-based recommendation automatically — nothing breaks. |
| `GEOAPIFY_API_KEY` | Optional | [geoapify.com](https://www.geoapify.com/) (free tier) | Enriches `/hotels` with live nearby hotel search. Dataset-based hotel pricing works with or without it. |
| `ORS_API_KEY` | Optional | [openrouteservice.org/dev/#/signup](https://openrouteservice.org/dev/#/signup) (free tier) | Powers the optional `/transport/route` live routing endpoint. **Note:** this must be a real OpenRouteService key — it looks different from an OpenRouter.ai key (which is for LLMs, not maps), so double-check you signed up on the right site. |

Your keys already went into `/home/claude/budget-agent/.env` in this build. Rotate
the Gemini key in AI Studio if you're at all unsure who's seen this conversation,
since keys typed into chat should be treated as potentially exposed.

## 2. Run with Docker (recommended, one command)

```bash
cd budget-agent
docker compose up --build
```

This starts:
- PostgreSQL on `localhost:5432`
- FastAPI backend on `localhost:8000` (docs at `localhost:8000/docs`)
- React frontend on `localhost:5173`

Open **http://localhost:5173** and start planning.

## 3. Run manually (without Docker)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Train the quick-estimate ML model (one-time, ~10 seconds)
python models/train_model.py

# Start Postgres yourself, or point DATABASE_URL in .env at any Postgres instance
uvicorn app:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Visit **http://localhost:5173**.

> If you don't want to set up Postgres locally, the API still works —
> `/calculate-budget` degrades gracefully and just skips saving history if the
> database isn't reachable.

## 4. API reference

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/calculate-budget` | Full budget calculation: breakdown, daily chart, savings suggestions, AI recommendation |
| POST | `/optimize-budget` | Just the optimizer step (savings suggestions + adjusted breakdown) |
| POST | `/predict-expense` | Instant ML-model cost estimate (no dataset lookups) |
| GET | `/hotels?destination=` | Hotel options from dataset (+ live Geoapify results if configured) |
| GET | `/restaurants?destination=` | Restaurant/food options from dataset |
| GET | `/weather?destination=` | Live weather via Open-Meteo (no key needed) |
| GET | `/currency?amount=&from=&to=` | Live currency conversion via Frankfurter (no key needed) |
| GET | `/transport?destination=` | Local transport options from dataset |
| GET | `/transport/route?...` | Live routing distance/duration via OpenRouteService |
| GET | `/destinations` | List of destinations covered by the datasets |
| GET | `/history?limit=` | Past budget calculations (requires Postgres) |

Full interactive docs: **http://localhost:8000/docs**

### Example request
```bash
curl -X POST http://localhost:8000/calculate-budget \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Ooty",
    "days": 4,
    "travelers": 2,
    "budget": 25000,
    "travel_style": "Standard"
  }'
```

## 5. Datasets included

10 Indian destinations, each with multiple entries across Budget/Standard/Luxury
tiers: **Ooty, Goa, Manali, Jaipur, Munnar, Coorg, Rishikesh, Pondicherry, Udaipur,
Darjeeling.**

- `datasets/hotels.csv` — per-night pricing, rating, occupancy
- `datasets/restaurants.csv` — per-person meal pricing by cuisine/category
- `datasets/tourism.csv` — attraction entry fees
- `datasets/fuel.csv` — local transport pricing by mode

Want more destinations? Just append rows following the same columns — nothing
else needs to change, the calculator reads destinations dynamically from the CSVs.

## 6. How the budget engine works

1. **Hotel** — average nightly rate for the chosen style × rooms needed × days
2. **Food** — average per-meal price × 3 meals × travelers × days
3. **Transport** — per-day local transport rate × travelers/vehicles × days
4. **Attractions** — sum of entry fees for a style-appropriate set of attractions × travelers
5. **Shopping** — 5–12% of the above subtotal, scaled by travel style
6. **Emergency buffer** — 10% of everything above
7. If total > budget → **optimizer** downgrades categories step by step (hotel →
   transport → food → shopping → attractions) until back on budget or a clear
   "still short" note is shown
8. **Gemini** turns the numbers into a natural-language recommendation using
   `prompts/budget_prompt.txt`; falls back to a rule-based summary if no key is set

## 7. Retraining the ML model

`services/predictor.py`'s `/predict-expense` endpoint uses a RandomForest model
trained on synthetic data generated by running the calculator engine across many
combinations. If you edit the datasets or calculator logic, retrain it:

```bash
cd backend
python models/train_model.py
```

## Tech stack

- **Frontend:** React + Vite + Tailwind CSS + Axios + Recharts
- **Backend:** FastAPI
- **Database:** PostgreSQL (via SQLAlchemy)
- **AI:** Gemini 2.5 Flash (Google AI Studio)
- **Maps & Places:** Geoapify + OpenRouteService
- **Weather:** Open-Meteo (free, no key)
- **Currency:** Frankfurter (free, no key)
