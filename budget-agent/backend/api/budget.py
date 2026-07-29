"""
POST /calculate-budget
POST /optimize-budget
POST /predict-expense

The core budget-planning endpoints. These orchestrate calculator -> optimizer ->
predictor (Gemini + ML model) and persist each request to PostgreSQL for history.
"""
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db, BudgetRequest
from services.calculator import calculate_full_budget
from services.optimizer import optimize_budget
from services.predictor import generate_ai_recommendation, predict_quick_estimate
from services.gemini_dataset import ensure_destination_data, get_destination_currency, normalize_destination_casing
from utils.helpers import list_destinations, load_csv

router = APIRouter(tags=["Budget Engine"])

TravelStyle = Literal["Budget", "Standard", "Luxury"]


class BudgetInput(BaseModel):
    destination: str = Field(..., examples=["Ooty"])
    days: int = Field(..., ge=1, le=30)
    travelers: int = Field(..., ge=1, le=20)
    budget: float = Field(..., gt=0)
    travel_style: TravelStyle = "Standard"
    sector_budgets: Optional[dict[str, float]] = None


class PredictInput(BaseModel):
    destination: str
    days: int = Field(..., ge=1, le=30)
    travelers: int = Field(..., ge=1, le=20)
    travel_style: TravelStyle = "Standard"


@router.get("/destinations")
def get_destinations():
    return {"destinations": list_destinations()}


@router.post("/calculate-budget")
def calculate_budget(payload: BudgetInput, db: Session = Depends(get_db)):
    ensure_destination_data(payload.destination)
    currency_info = get_destination_currency(payload.destination)

    # Sum up custom sector budgets if provided
    total_budget = payload.budget
    if payload.sector_budgets:
        total_budget = sum(payload.sector_budgets.values())

    try:
        result = calculate_full_budget(
            payload.destination, payload.days, payload.travelers,
            total_budget, payload.travel_style,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    opt = optimize_budget(result, sector_budgets=payload.sector_budgets)

    ai = generate_ai_recommendation(
        destination=payload.destination,
        days=payload.days,
        travelers=payload.travelers,
        budget=total_budget,
        travel_style=payload.travel_style,
        breakdown=result["breakdown"],
        total_cost=result["total_estimated_cost"],
    )

    # Load details lists for this destination to display in frontend
    try:
        hotels_df = load_csv("hotels.csv")
        dest_hotels = hotels_df[hotels_df["destination"].str.lower() == payload.destination.lower()].to_dict(orient="records")
    except Exception:
        dest_hotels = []

    try:
        rest_df = load_csv("restaurants.csv")
        dest_rests = rest_df[rest_df["destination"].str.lower() == payload.destination.lower()].to_dict(orient="records")
    except Exception:
        dest_rests = []

    try:
        trans_df = load_csv("fuel.csv")
        dest_trans = trans_df[trans_df["destination"].str.lower() == payload.destination.lower()].to_dict(orient="records")
    except Exception:
        dest_trans = []

    try:
        tour_df = load_csv("tourism.csv")
        dest_tours = tour_df[tour_df["destination"].str.lower() == payload.destination.lower()].to_dict(orient="records")
    except Exception:
        dest_tours = []

    response = {
        **result,
        "savings_suggestions": opt["suggestions"],
        "ai_recommendation": ai,
        "currency_info": currency_info,
        "sector_budgets": payload.sector_budgets,
        "details": {
            "hotels": dest_hotels,
            "restaurants": dest_rests,
            "transport": dest_trans,
            "attractions": dest_tours,
        }
    }

    # Persist to PostgreSQL history
    try:
        record = BudgetRequest(
            destination=payload.destination,
            days=payload.days,
            travelers=payload.travelers,
            budget=total_budget,
            travel_style=payload.travel_style,
            total_estimated_cost=result["total_estimated_cost"],
            remaining=result["remaining"],
            breakdown=result["breakdown"],
            daily_breakdown=result["daily_breakdown"],
            recommendations=opt["suggestions"],
            ai_recommendation_text=ai["text"],
        )
        db.add(record)
        db.commit()
    except Exception:
        db.rollback()  # DB being unreachable should never break the API response

    return response


@router.post("/optimize-budget")
def optimize_budget_endpoint(payload: BudgetInput):
    payload.destination = normalize_destination_casing(payload.destination)
    ensure_destination_data(payload.destination)
    
    total_budget = payload.budget
    if payload.sector_budgets:
        total_budget = sum(payload.sector_budgets.values())

    try:
        result = calculate_full_budget(
            payload.destination, payload.days, payload.travelers,
            total_budget, payload.travel_style,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    opt = optimize_budget(result, sector_budgets=payload.sector_budgets)
    return opt


@router.post("/predict-expense")
def predict_expense(payload: PredictInput):
    payload.destination = normalize_destination_casing(payload.destination)
    quick_estimate = predict_quick_estimate(
        payload.destination, payload.days, payload.travelers, payload.travel_style
    )
    if quick_estimate is None:
        raise HTTPException(
            status_code=503,
            detail="Prediction model not found. Run backend/models/train_model.py first.",
        )
    return {
        "destination": payload.destination,
        "days": payload.days,
        "travelers": payload.travelers,
        "travel_style": payload.travel_style,
        "predicted_total_cost": quick_estimate,
    }


@router.get("/history")
def get_history(limit: int = 10, db: Session = Depends(get_db)):
    try:
        rows = (
            db.query(BudgetRequest)
            .order_by(BudgetRequest.created_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "history": [
                {
                    "id": r.id,
                    "destination": r.destination,
                    "days": r.days,
                    "travelers": r.travelers,
                    "budget": r.budget,
                    "travel_style": r.travel_style,
                    "total_estimated_cost": r.total_estimated_cost,
                    "remaining": r.remaining,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in rows
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")


@router.get("/history/{record_id}")
def get_history_detail(record_id: int, db: Session = Depends(get_db)):
    try:
        r = db.query(BudgetRequest).filter(BudgetRequest.id == record_id).first()
        if not r:
            raise HTTPException(status_code=404, detail="History record not found")

        # Load details lists for this destination to display in frontend
        try:
            hotels_df = load_csv("hotels.csv")
            dest_hotels = hotels_df[hotels_df["destination"].str.lower() == r.destination.lower()].to_dict(orient="records")
        except Exception:
            dest_hotels = []

        try:
            rest_df = load_csv("restaurants.csv")
            dest_rests = rest_df[rest_df["destination"].str.lower() == r.destination.lower()].to_dict(orient="records")
        except Exception:
            dest_rests = []

        try:
            trans_df = load_csv("fuel.csv")
            dest_trans = trans_df[trans_df["destination"].str.lower() == r.destination.lower()].to_dict(orient="records")
        except Exception:
            dest_trans = []

        try:
            tour_df = load_csv("tourism.csv")
            dest_tours = tour_df[tour_df["destination"].str.lower() == r.destination.lower()].to_dict(orient="records")
        except Exception:
            dest_tours = []

        return {
            "id": r.id,
            "destination": r.destination,
            "days": r.days,
            "travelers": r.travelers,
            "budget": r.budget,
            "travel_style": r.travel_style,
            "total_estimated_cost": r.total_estimated_cost,
            "remaining": r.remaining,
            "breakdown": r.breakdown,
            "daily_breakdown": r.daily_breakdown,
            "recommendations": r.recommendations,
            "ai_recommendation_text": r.ai_recommendation_text,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "currency_info": get_destination_currency(r.destination),
            "details": {
                "hotels": dest_hotels,
                "restaurants": dest_rests,
                "transport": dest_trans,
                "attractions": dest_tours,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")
