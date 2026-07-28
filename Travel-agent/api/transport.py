import requests
import math
from config import OPENROUTE_API_KEY, OPENROUTE_URL
from api.traffic import TRAFFIC_MULTIPLIER

# Cost per km estimates (USD)
COST_PER_KM = {
    "walking": 0, "bike": 0.05, "bus": 0.08,
    "metro": 0.12, "train": 0.18, "taxi": 0.85,
    "rental_car": 0.45, "flight": 2.50
}

BASE_SPEED_KMH = {
    "walking": 5, "bike": 15, "bus": 30,
    "metro": 45, "train": 90, "taxi": 50,
    "rental_car": 80, "flight": 700
}

def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def get_ors_route(src_lat, src_lon, dst_lat, dst_lon, profile="driving-car") -> dict:
    try:
        url = f"{OPENROUTE_URL}/{profile}"
        resp = requests.post(url, json={
            "coordinates": [[src_lon, src_lat], [dst_lon, dst_lat]],
            "radiuses": [-1, -1]   # snap to nearest routable point automatically
        }, headers={
            "Authorization": OPENROUTE_API_KEY,
            "Content-Type": "application/json"
        }, timeout=15)
        if resp.status_code == 200:
            seg = resp.json()["routes"][0]["summary"]
            return {"distance": seg["distance"] / 1000, "duration": seg["duration"] / 60}
    except Exception:
        pass
    return None

def get_transport_options(src_lat, src_lon, dst_lat, dst_lon, traffic: str, group_size: int) -> list:
    dist = haversine(src_lat, src_lon, dst_lat, dst_lon)
    multiplier = TRAFFIC_MULTIPLIER.get(traffic, 1.0)
    options = []

    # Try ORS for driving
    ors = get_ors_route(src_lat, src_lon, dst_lat, dst_lon)

    for mode, speed in BASE_SPEED_KMH.items():
        if dist < 1 and mode not in ["walking", "bike"]:
            continue
        if dist > 500 and mode in ["walking", "bike", "bus", "metro"]:
            continue
        if dist < 50 and mode == "flight":
            continue

        if mode in ["taxi", "rental_car"] and ors:
            duration = ors["duration"] * multiplier
            distance = ors["distance"]
        else:
            road_factor = 1.3 if mode not in ["flight"] else 1.0
            duration = (dist * road_factor / speed) * 60 * (multiplier if mode in ["taxi","bus","rental_car"] else 1.0)
            distance = dist * road_factor if mode != "flight" else dist

        cost = distance * COST_PER_KM[mode] * group_size
        if mode == "flight":
            cost = max(cost, 80 * group_size)

        transfers = 0
        if mode == "train" and dist > 100: transfers = 1
        if mode == "bus" and dist > 80: transfers = 1
        if mode == "metro": transfers = max(0, int(dist / 20) - 1)

        options.append({
            "mode": mode.replace("_", " ").title(),
            "duration": round(duration),
            "distance": round(distance, 1),
            "cost": round(cost, 2),
            "transfers": transfers,
            "availability": True,
            "eco_friendly": mode in ["walking", "bike", "metro", "train", "bus"],
            "scenic": mode in ["rental_car", "bike", "walking"]
        })

    return options
