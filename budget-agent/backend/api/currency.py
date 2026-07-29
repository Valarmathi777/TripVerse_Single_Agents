"""GET /currency - live currency conversion via Frankfurter (free, no API key)."""
from fastapi import APIRouter, HTTPException, Query
import httpx

from config import settings

router = APIRouter(tags=["Currency"])


@router.get("/currency")
def get_currency(
    amount: float = Query(1.0, description="Amount to convert"),
    from_currency: str = Query("INR", alias="from"),
    to_currency: str = Query("USD", alias="to"),
):
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(settings.FRANKFURTER_BASE_URL, params={
                "base": from_currency.upper(),
                "symbols": to_currency.upper(),
            })
            resp.raise_for_status()
            data = resp.json()
            rate = data.get("rates", {}).get(to_currency.upper())
            if rate is None:
                raise HTTPException(status_code=400, detail="Unsupported currency pair")

        return {
            "amount": amount,
            "from": from_currency.upper(),
            "to": to_currency.upper(),
            "rate": rate,
            "converted_amount": round(amount * rate, 2),
            "date": data.get("date"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Currency service unavailable: {e}")
