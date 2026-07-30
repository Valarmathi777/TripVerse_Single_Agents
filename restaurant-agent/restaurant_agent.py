from typing import Union, Dict, Any
from models.restaurant import UserPreference, RecommendationResponse
from services.restaurant_service import restaurant_service

class RestaurantAgent:
    """
    Enterprise Professional Restaurant Recommendation AI Agent.
    Coordinates sub-agent components (Preference Parser, Recommender, Ranking, Explanation)
    with detailed reasoning traces, performance metrics, and dual sync/async pipelines.
    """

    def recommend(self, user_input: Union[str, Dict[str, Any], UserPreference]) -> RecommendationResponse:
        """Executes end-to-end recommendation workflow synchronously."""
        return restaurant_service.process_recommendation(user_input)

    async def recommend_async(self, user_input: Union[str, Dict[str, Any], UserPreference]) -> RecommendationResponse:
        """Executes end-to-end recommendation workflow asynchronously."""
        return await restaurant_service.process_recommendation_async(user_input)

# Default global instance
restaurant_agent = RestaurantAgent()

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    query = "I need cheap vegetarian food in Tokyo"
    print(f"Executing Professional Restaurant Agent for query: '{query}'\n")
    response = restaurant_agent.recommend(query)
    print(response.formatted_output)
    print("\n--- AGENT REASONING TRACE ---")
    for step in response.agent_trace:
        print(f"[{step.agent_name}] ({step.duration_ms}ms) -> {step.action}: {step.output_summary}")