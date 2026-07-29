"""Shared helper utilities used across api/ and services/ modules."""
import functools
from pathlib import Path
import pandas as pd

from config import settings


@functools.lru_cache(maxsize=8)
def load_csv(filename: str) -> pd.DataFrame:
    """
    Load a dataset CSV once and cache it in memory.
    filename e.g. 'hotels.csv', 'restaurants.csv', 'tourism.csv', 'fuel.csv'
    """
    path: Path = settings.DATASETS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    return pd.read_csv(path)


def format_inr(amount: float) -> str:
    """Format a number as an Indian Rupee string with lakh/crore-style commas."""
    amount = round(amount)
    s = str(abs(amount))
    if len(s) <= 3:
        formatted = s
    else:
        last3 = s[-3:]
        rest = s[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        formatted = ",".join(parts) + "," + last3
    sign = "-" if amount < 0 else ""
    return f"{sign}₹{formatted}"


def list_destinations() -> list:
    """Return the sorted list of destinations available across all datasets."""
    hotels = load_csv("hotels.csv")
    return sorted(hotels["destination"].unique().tolist())


def rooms_required(travelers: int, max_occupancy_default: int = 2) -> int:
    """Simple room calculation - 2 travelers per room by default."""
    import math
    return max(1, math.ceil(travelers / max_occupancy_default))
