from pydantic import BaseModel
from typing import List, Optional

class TravelRequest(BaseModel):
    source: str
    destination: str
    date: str
    time: str
    budget: float
    group_size: int
    preference: str = "fastest"

class TransportOption(BaseModel):
    mode: str
    duration: int        # minutes
    distance: float      # km
    cost: float
    transfers: int
    availability: bool = True
    eco_friendly: bool = False
    scenic: bool = False

class RouteRecommendation(BaseModel):
    recommended_mode: str
    travel_time: str
    estimated_cost: float
    distance: str
    arrival: str
    score: float
    reason: List[str]
    all_options: Optional[List[dict]] = []
    weather: Optional[dict] = {}
    traffic: Optional[str] = "unknown"
