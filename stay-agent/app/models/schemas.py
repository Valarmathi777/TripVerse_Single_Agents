from pydantic import BaseModel, Field

class StayRequest(BaseModel):
    destination: str
    checkin: str
    checkout: str
    guests: int
    budget: str
    travel_style: str
    accommodation: str
    requirements: str

class NotesUpdateRequest(BaseModel):
    notes: str

class RatingUpdateRequest(BaseModel):
    rating: int = Field(..., ge=0, le=5)
