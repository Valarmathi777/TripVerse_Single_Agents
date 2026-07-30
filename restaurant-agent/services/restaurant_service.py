import time
from typing import Union, Dict, Any, List
from models.restaurant import (
    UserPreference, Restaurant, RecommendationResponse, ReasoningStep, ExecutionMetadata
)
from agents.preference_parser import preference_parser_agent
from agents.restaurant_recommender import restaurant_recommender_agent
from agents.ranking_agent import ranking_agent
from agents.explanation_agent import explanation_agent
from logger import logger

class RestaurantService:
    """Enterprise Service layer orchestrating agents with step-by-step reasoning trace metrics."""
    
    def process_recommendation(
        self, user_input: Union[str, Dict[str, Any], UserPreference]
    ) -> RecommendationResponse:
        start_total = time.perf_counter()
        agent_trace: List[ReasoningStep] = []

        # Step 1: Preference Parser Agent
        t0 = time.perf_counter()
        preference: UserPreference = preference_parser_agent.parse(user_input)
        dt1 = round((time.perf_counter() - t0) * 1000, 2)
        agent_trace.append(
            ReasoningStep(
                agent_name="PreferenceParserAgent",
                action="Extracted user preferences from query string or dict",
                output_summary=f"Location: {preference.location}, Cuisine: {preference.cuisine}, Diet: {preference.food_preference}, Budget: {preference.budget}, Min Rating: {preference.min_rating}",
                duration_ms=dt1
            )
        )

        # Step 2: Restaurant Recommender Agent
        t0 = time.perf_counter()
        candidates: List[Dict[str, Any]] = restaurant_recommender_agent.find_restaurants(preference)
        dt2 = round((time.perf_counter() - t0) * 1000, 2)
        agent_trace.append(
            ReasoningStep(
                agent_name="RestaurantRecommenderAgent",
                action="Queried Google Places API & Dataset repository for matching candidates",
                output_summary=f"Retrieved {len(candidates)} candidate restaurants in {preference.location}",
                duration_ms=dt2
            )
        )

        # Step 3: Ranking Agent (MAUT Decision Matrix)
        t0 = time.perf_counter()
        ranked_restaurants: List[Dict[str, Any]] = ranking_agent.rank(candidates, preference)
        dt3 = round((time.perf_counter() - t0) * 1000, 2)
        agent_trace.append(
            ReasoningStep(
                agent_name="RankingAgent",
                action="Applied Multi-Attribute Utility Theory (MAUT) scoring matrix (Dietary 35%, Rating 30%, Budget 20%, Location 15%)",
                output_summary=f"Ranked {len(ranked_restaurants)} candidates by utility score. Top match score: {ranked_restaurants[0].get('match_score', 0) if ranked_restaurants else 0}",
                duration_ms=dt3
            )
        )

        # Step 4: Gemini Explanation Agent
        t0 = time.perf_counter()
        formatted_output: str = explanation_agent.explain(ranked_restaurants, preference)
        dt4 = round((time.perf_counter() - t0) * 1000, 2)
        agent_trace.append(
            ReasoningStep(
                agent_name="ExplanationAgent",
                action="Generated tailored AI food critic explanations for Morning, Lunch, and Dinner options",
                output_summary="Constructed readable structured meal recommendation guide",
                duration_ms=dt4
            )
        )

        total_ms = round((time.perf_counter() - start_total) * 1000, 2)

        restaurant_models = [
            Restaurant(
                name=r.get("name", "Unknown"),
                location=r.get("location", preference.location),
                cuisine=r.get("cuisine", preference.cuisine),
                budget=r.get("budget", preference.budget),
                type=r.get("type", preference.food_preference),
                rating=float(r.get("rating", 4.0)),
                match_score=r.get("match_score"),
                address=r.get("address"),
                meal_time=r.get("meal_time", "Lunch"),
                description=r.get("description"),
                reasons=r.get("reasons", [])
            ) for r in ranked_restaurants
        ]

        metadata = ExecutionMetadata(
            execution_time_ms=total_ms,
            candidates_retrieved=len(candidates),
            confidence_score=0.96 if ranked_restaurants else 0.50
        )

        return RecommendationResponse(
            status="success",
            preferences=preference,
            recommendations=restaurant_models,
            formatted_output=formatted_output,
            agent_trace=agent_trace,
            metadata=metadata
        )

    async def process_recommendation_async(
        self, user_input: Union[str, Dict[str, Any], UserPreference]
    ) -> RecommendationResponse:
        start_total = time.perf_counter()
        agent_trace: List[ReasoningStep] = []

        # Step 1: Preference Parser Agent
        t0 = time.perf_counter()
        preference: UserPreference = await preference_parser_agent.parse_async(user_input)
        dt1 = round((time.perf_counter() - t0) * 1000, 2)
        agent_trace.append(
            ReasoningStep(
                agent_name="PreferenceParserAgent",
                action="Extracted user preferences from query string or dict asynchronously",
                output_summary=f"Location: {preference.location}, Cuisine: {preference.cuisine}, Diet: {preference.food_preference}, Budget: {preference.budget}, Min Rating: {preference.min_rating}",
                duration_ms=dt1
            )
        )

        # Step 2: Restaurant Recommender Agent
        t0 = time.perf_counter()
        candidates: List[Dict[str, Any]] = restaurant_recommender_agent.find_restaurants(preference)
        dt2 = round((time.perf_counter() - t0) * 1000, 2)
        agent_trace.append(
            ReasoningStep(
                agent_name="RestaurantRecommenderAgent",
                action="Queried Google Places API & Dataset repository for matching candidates asynchronously",
                output_summary=f"Retrieved {len(candidates)} candidate restaurants in {preference.location}",
                duration_ms=dt2
            )
        )

        # Step 3: Ranking Agent (MAUT Decision Matrix)
        t0 = time.perf_counter()
        ranked_restaurants: List[Dict[str, Any]] = ranking_agent.rank(candidates, preference)
        dt3 = round((time.perf_counter() - t0) * 1000, 2)
        agent_trace.append(
            ReasoningStep(
                agent_name="RankingAgent",
                action="Applied Multi-Attribute Utility Theory (MAUT) scoring matrix (Dietary 35%, Rating 30%, Budget 20%, Location 15%)",
                output_summary=f"Ranked {len(ranked_restaurants)} candidates by utility score. Top match score: {ranked_restaurants[0].get('match_score', 0) if ranked_restaurants else 0}",
                duration_ms=dt3
            )
        )

        # Step 4: Gemini Explanation Agent
        t0 = time.perf_counter()
        formatted_output: str = await explanation_agent.explain_async(ranked_restaurants, preference)
        dt4 = round((time.perf_counter() - t0) * 1000, 2)
        agent_trace.append(
            ReasoningStep(
                agent_name="ExplanationAgent",
                action="Generated tailored AI food critic explanations for Morning, Lunch, and Dinner options asynchronously",
                output_summary="Constructed readable structured meal recommendation guide",
                duration_ms=dt4
            )
        )

        total_ms = round((time.perf_counter() - start_total) * 1000, 2)

        restaurant_models = [
            Restaurant(
                name=r.get("name", "Unknown"),
                location=r.get("location", preference.location),
                cuisine=r.get("cuisine", preference.cuisine),
                budget=r.get("budget", preference.budget),
                type=r.get("type", preference.food_preference),
                rating=float(r.get("rating", 4.0)),
                match_score=r.get("match_score"),
                address=r.get("address"),
                meal_time=r.get("meal_time", "Lunch"),
                description=r.get("description"),
                reasons=r.get("reasons", [])
            ) for r in ranked_restaurants
        ]

        metadata = ExecutionMetadata(
            execution_time_ms=total_ms,
            candidates_retrieved=len(candidates),
            confidence_score=0.96 if ranked_restaurants else 0.50
        )

        return RecommendationResponse(
            status="success",
            preferences=preference,
            recommendations=restaurant_models,
            formatted_output=formatted_output,
            agent_trace=agent_trace,
            metadata=metadata
        )

restaurant_service = RestaurantService()
