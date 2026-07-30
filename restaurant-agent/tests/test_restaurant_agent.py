import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from app import app
from models.restaurant import UserPreference
from agents.preference_parser import preference_parser_agent
from agents.ranking_agent import ranking_agent
from restaurant_agent import restaurant_agent
from utils import sort_by_rating, remove_duplicates


def test_preference_parser_sync():
    query = "I need cheap vegetarian food in Tokyo"
    pref = preference_parser_agent.parse(query)
    assert pref.location.lower() == "tokyo"
    assert pref.food_preference.lower() == "vegetarian"
    assert pref.budget.lower() == "low"


def test_preference_parser_async():
    query = "I need cheap vegetarian food in Tokyo"
    pref = asyncio.run(preference_parser_agent.parse_async(query))
    assert pref.location.lower() == "tokyo"
    assert pref.food_preference.lower() == "vegetarian"


def test_maut_decision_matrix_ranking():
    pref = UserPreference(location="Tokyo", budget="Low", food_preference="Vegetarian", min_rating=4.0)
    candidates = [
        {"name": "Resto High NonVeg", "location": "Tokyo", "budget": "High", "type": "Non-Vegetarian", "rating": 4.9},
        {"name": "Resto Low Veg", "location": "Tokyo", "budget": "Low", "type": "Vegetarian", "rating": 4.6}
    ]
    ranked = ranking_agent.rank(candidates, pref)
    assert len(ranked) == 2
    assert ranked[0]["name"] == "Resto Low Veg"
    assert ranked[0]["match_score"] > ranked[1]["match_score"]


def test_restaurant_agent_sync():
    query = "I need cheap vegetarian food in Tokyo"
    result = restaurant_agent.recommend(query)
    assert result.status == "success"
    assert len(result.recommendations) > 0
    assert len(result.agent_trace) == 4
    assert result.metadata.execution_time_ms > 0


def test_restaurant_agent_async():
    query = "I need cheap vegetarian food in Tokyo"
    result = asyncio.run(restaurant_agent.recommend_async(query))
    assert result.status == "success"
    assert len(result.recommendations) > 0
    assert len(result.agent_trace) == 4


@pytest.mark.anyio
async def test_fastapi_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/")
        assert r.status_code == 200

        r = await client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

        r = await client.post("/api/recommend", json={"query": "cheap vegetarian food in Tokyo"})
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "agent_trace" in data
        assert "metadata" in data
