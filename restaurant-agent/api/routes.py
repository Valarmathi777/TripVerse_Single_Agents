from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from models.restaurant import RecommendationRequest, RecommendationResponse
from restaurant_agent import restaurant_agent
from database import get_db, RestaurantDB
from exceptions import RestaurantAgentException
from logger import logger

router = APIRouter()


class RestaurantCreate(BaseModel):
    name: str
    location: str
    country: Optional[str] = None
    cuisine: str = "Any"
    budget: str = "Any"
    type: str = "Any"
    rating: float = 4.0
    meal_time: str = "Lunch"
    address: Optional[str] = None
    description: Optional[str] = None

class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    country: Optional[str] = None
    cuisine: Optional[str] = None
    budget: Optional[str] = None
    type: Optional[str] = None
    rating: Optional[float] = None
    meal_time: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None


@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "ProfessionalRestaurantAgent", "version": "1.0.0"}


@router.get("/restaurants", tags=["Restaurants"])
def list_restaurants(
    location: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    q = db.query(RestaurantDB)
    if location:
        q = q.filter(RestaurantDB.location.ilike(f"%{location}%"))
    if country:
        q = q.filter(RestaurantDB.country.ilike(f"%{country}%"))
    if cuisine:
        q = q.filter(RestaurantDB.cuisine.ilike(f"%{cuisine}%"))
    if type:
        q = q.filter(RestaurantDB.type.ilike(f"%{type}%"))
    return [_to_dict(r) for r in q.all()]


@router.get("/countries", tags=["Restaurants"])
def list_countries(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all countries with their restaurant count."""
    rows = db.query(RestaurantDB).all()
    country_map: Dict[str, Dict] = {}
    for r in rows:
        c = r.country or "Unknown"
        if c not in country_map:
            country_map[c] = {"country": c, "count": 0, "cities": set(), "cuisines": set()}
        country_map[c]["count"] += 1
        if r.location:
            country_map[c]["cities"].add(r.location)
        if r.cuisine:
            country_map[c]["cuisines"].add(r.cuisine)
    result = []
    for k, v in country_map.items():
        result.append({
            "country": v["country"],
            "count": v["count"],
            "cities": sorted(list(v["cities"])),
            "cuisines": sorted(list(v["cuisines"]))
        })
    result.sort(key=lambda x: x["count"], reverse=True)
    return result


@router.post("/restaurants", tags=["Restaurants"], status_code=status.HTTP_201_CREATED)
def create_restaurant(payload: RestaurantCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    row = RestaurantDB(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_dict(row)


@router.put("/restaurants/{restaurant_id}", tags=["Restaurants"])
def update_restaurant(restaurant_id: int, payload: RestaurantUpdate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    row = db.query(RestaurantDB).filter(RestaurantDB.id == restaurant_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return _to_dict(row)


@router.delete("/restaurants/{restaurant_id}", tags=["Restaurants"])
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    row = db.query(RestaurantDB).filter(RestaurantDB.id == restaurant_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    db.delete(row)
    db.commit()
    return {"message": f"Restaurant '{row.name}' deleted successfully"}


@router.post("/recommend", response_model=RecommendationResponse, tags=["Recommendation"])
async def get_recommendations(request: RecommendationRequest):
    try:
        if request.query:
            return await restaurant_agent.recommend_async(request.query)
        elif request.preferences:
            return await restaurant_agent.recommend_async(request.preferences)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide 'query' or 'preferences'.")
    except RestaurantAgentException as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Internal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _to_dict(r: RestaurantDB) -> Dict[str, Any]:
    return {
        "id": r.id, "name": r.name, "location": r.location,
        "country": r.country,
        "cuisine": r.cuisine, "budget": r.budget, "type": r.type,
        "rating": r.rating, "meal_time": r.meal_time,
        "address": r.address, "description": r.description,
    }
