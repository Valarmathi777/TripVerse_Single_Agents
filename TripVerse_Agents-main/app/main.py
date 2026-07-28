from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .plan_agent import generate_plan
from .database import init_db, save_trip, get_all_trips, delete_trip

# Initialize the database on startup
init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PlanRequest(BaseModel):
    destination: str
    days: int
    interests: str
    must_include: str = ""

class TripUpdateRequest(BaseModel):
    destination: str
    days: int
    interests: str
    must_include: str = ""
    plan: dict

class RegenerateRequest(BaseModel):
    destination: str
    days: int
    interests: str
    must_include: str = ""

@app.post("/plan")
def get_plan(request: PlanRequest):
    try:
        # Generate the plan from the LLM
        plan_data = generate_plan(request.destination, request.days, request.interests, request.must_include)
        
        # Save to database
        trip_id = save_trip(request.destination, request.days, request.interests, request.must_include, plan_data)
        
        # Return the saved trip structure
        return {
            "id": trip_id,
            "destination": request.destination,
            "days": request.days,
            "interests": request.interests,
            "must_include": request.must_include,
            "plan": plan_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/trips/{trip_id}")
def update_existing_trip(trip_id: int, request: TripUpdateRequest):
    try:
        from .database import update_trip
        success = update_trip(trip_id, request.destination, request.days, request.interests, request.must_include, request.plan)
        if not success:
            raise HTTPException(status_code=404, detail="Trip not found")
        return {"message": "Trip updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trips/{trip_id}/regenerate")
def regenerate_trip(trip_id: int, request: RegenerateRequest):
    try:
        # Generate the plan from the LLM
        plan_data = generate_plan(request.destination, request.days, request.interests, request.must_include)
        
        # Save to database
        from .database import update_trip
        success = update_trip(trip_id, request.destination, request.days, request.interests, request.must_include, plan_data)
        if not success:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        return {
            "id": trip_id,
            "destination": request.destination,
            "days": request.days,
            "interests": request.interests,
            "must_include": request.must_include,
            "plan": plan_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trips/{trip_id}/recommendations")
def get_trip_recommendations(trip_id: int):
    try:
        from .database import get_db_connection
        conn = get_db_connection()
        row = conn.execute("SELECT destination, interests FROM trips WHERE id = ?", (trip_id,)).fetchone()
        conn.close()
        if not row:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        from .plan_agent import generate_recommendations
        recs = generate_recommendations(row["destination"], row["interests"])
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/trips")
def list_trips():
    try:
        return get_all_trips()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/trips/{trip_id}")
def remove_trip(trip_id: int):
    try:
        success = delete_trip(trip_id)
        if not success:
            raise HTTPException(status_code=404, detail="Trip not found")
        return {"message": "Trip deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))