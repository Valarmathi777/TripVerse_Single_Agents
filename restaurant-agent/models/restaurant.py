from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ReasoningStep(BaseModel):
    agent_name: str = Field(description="Name of the agent executing the step")
    action: str = Field(description="Action description")
    output_summary: str = Field(description="Summary of the step result")
    duration_ms: float = Field(default=0.0, description="Step duration in milliseconds")

class ExecutionMetadata(BaseModel):
    execution_time_ms: float = Field(default=0.0, description="Total execution time in milliseconds")
    candidates_retrieved: int = Field(default=0, description="Total candidates retrieved before ranking")
    confidence_score: float = Field(default=0.95, description="Overall recommendation confidence score (0.0 - 1.0)")

class UserPreference(BaseModel):
    location: str = Field(default="Tokyo", description="Target city or location")
    cuisine: str = Field(default="Any", description="Preferred cuisine (e.g., Japanese, Italian, Any)")
    budget: str = Field(default="Any", description="Budget level (Low, Medium, High, Any)")
    food_preference: str = Field(default="Any", description="Dietary requirement (Vegetarian, Non-Vegetarian, Vegan, Halal, Any)")
    min_rating: float = Field(default=4.0, description="Minimum acceptable rating")
    meal_time: Optional[str] = Field(default=None, description="Preferred meal time (Morning, Lunch, Dinner)")
    query: Optional[str] = Field(default=None, description="Original natural language user query")

class Restaurant(BaseModel):
    name: str
    location: str
    cuisine: str
    budget: str
    type: str
    rating: float
    match_score: Optional[float] = None
    address: Optional[str] = None
    meal_time: Optional[str] = "Lunch"
    description: Optional[str] = None
    reasons: Optional[List[str]] = Field(default_factory=list)

class RecommendationRequest(BaseModel):
    query: Optional[str] = Field(default=None, description="Free-text query, e.g. 'I need cheap vegetarian food in Tokyo'")
    preferences: Optional[UserPreference] = None

class RecommendationResponse(BaseModel):
    status: str = "success"
    preferences: UserPreference
    recommendations: List[Restaurant]
    formatted_output: str
    agent_trace: List[ReasoningStep] = Field(default_factory=list)
    metadata: ExecutionMetadata = Field(default_factory=ExecutionMetadata)
