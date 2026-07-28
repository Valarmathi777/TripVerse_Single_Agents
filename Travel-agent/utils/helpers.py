import requests
from config import NOMINATIM_URL

def geocode(location: str) -> tuple:
    try:
        resp = requests.get(NOMINATIM_URL, params={
            "q": location, "format": "json", "limit": 1
        }, headers={"User-Agent": "MoveAgent/1.0"}, timeout=10)
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None

def minutes_to_hm(minutes: int) -> str:
    h, m = divmod(int(minutes), 60)
    return f"{h}h {m:02d}m" if h else f"{m}m"

def add_minutes_to_time(base_time: str, minutes: int) -> str:
    from datetime import datetime, timedelta
    try:
        t = datetime.strptime(base_time, "%H:%M")
        t += timedelta(minutes=minutes)
        return t.strftime("%H:%M")
    except Exception:
        return "N/A"
