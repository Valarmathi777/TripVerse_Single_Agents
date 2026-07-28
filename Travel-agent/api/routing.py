from fastapi import APIRouter, HTTPException
from models.schemas import TravelRequest
from utils.helpers import geocode
from api.transport import get_transport_options
from api.weather import get_weather
from api.traffic import get_traffic_level
from planner.route_finder import filter_options
from planner.optimizer import optimize_and_recommend

router = APIRouter()

@router.post("/plan")
def plan_route(req: TravelRequest):
    src_lat, src_lon = geocode(req.source)
    dst_lat, dst_lon = geocode(req.destination)

    if not src_lat or not dst_lat:
        raise HTTPException(status_code=400, detail="Could not geocode one or both locations.")

    weather = get_weather(dst_lat, dst_lon)
    traffic = get_traffic_level(src_lat, src_lon)

    options = get_transport_options(src_lat, src_lon, dst_lat, dst_lon, traffic, req.group_size)
    valid = filter_options(options, req.budget, req.group_size, weather)

    if not valid:
        raise HTTPException(status_code=404, detail="No valid routes found within your constraints.")

    result = optimize_and_recommend(valid, req.preference, traffic, req.budget, req.time)
    result["weather"] = weather
    result["traffic"] = traffic
    result["source"] = req.source
    result["destination"] = req.destination
    return result
