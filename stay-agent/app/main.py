import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import StayRequest, NotesUpdateRequest, RatingUpdateRequest
from app.agents.stay_agent import generate_stay
import app.services.database as db

app = FastAPI(title="TripVerse Stay Agent API")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure database is initialized on startup
@app.on_event("startup")
def startup_event():
    db.init_db()

@app.post("/stay")
def stay(request: StayRequest):
    return generate_stay(
        request.destination,
        request.checkin,
        request.checkout,
        request.guests,
        request.budget,
        request.travel_style,
        request.accommodation,
        request.requirements,
    )

@app.get("/stays")
def get_all_stays(
    search: str = Query(None, description="Search by destination"),
    bookmarked: bool = Query(False, description="Filter only bookmarked stays")
):
    return db.get_all_stays(search_query=search, filter_bookmarked=bookmarked)

@app.get("/stays/{stay_id}")
def get_stay_by_id(stay_id: int):
    stay_record = db.get_stay_by_id(stay_id)
    if not stay_record:
        raise HTTPException(status_code=404, detail="Stay not found")
    return stay_record

@app.delete("/stays/{stay_id}")
def delete_stay_record(stay_id: int):
    success = db.delete_stay(stay_id)
    if not success:
        raise HTTPException(status_code=404, detail="Stay not found")
    return {"status": "success", "message": "Stay deleted successfully"}

@app.post("/stays/{stay_id}/bookmark")
def toggle_bookmark_status(stay_id: int):
    result = db.toggle_bookmark(stay_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result

@app.put("/stays/{stay_id}/notes")
def update_stay_notes(stay_id: int, request: NotesUpdateRequest):
    success = db.update_notes(stay_id, request.notes)
    if not success:
        raise HTTPException(status_code=404, detail="Stay not found")
    return {"status": "success", "message": "Notes updated successfully"}

@app.put("/stays/{stay_id}/rating")
def update_stay_rating(stay_id: int, request: RatingUpdateRequest):
    success = db.update_rating(stay_id, request.rating)
    if not success:
        raise HTTPException(status_code=404, detail="Stay not found")
    return {"status": "success", "message": "Rating updated successfully"}

@app.get("/statistics")
def get_statistics():
    return db.get_stats()

@app.post("/debug-log")
async def debug_log(data: dict):
    print("\n================ BROWSER JS ERROR ================")
    import json
    print(json.dumps(data, indent=2))
    print("==================================================\n")
    return {"status": "ok"}

# Mount the static directory
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Serve UI at index page
@app.get("/")
def read_root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Welcome to TripVerse Stay Agent API. Frontend is being set up."}
