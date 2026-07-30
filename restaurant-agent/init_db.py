import json
import os
from database import create_tables, SessionLocal, RestaurantDB

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "restaurants.json")


def seed():
    create_tables()
    db = SessionLocal()
    try:
        if db.query(RestaurantDB).count() > 0:
            print("Database already seeded.")
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        for r in data:
            db.add(RestaurantDB(
                name=r.get("name"),
                location=r.get("location"),
                country=r.get("country"),
                cuisine=r.get("cuisine", "Any"),
                budget=r.get("budget", "Any"),
                type=r.get("type", "Any"),
                rating=float(r.get("rating", 4.0)),
                meal_time=r.get("meal_time", "Lunch"),
                address=r.get("address"),
                description=r.get("description"),
            ))
        db.commit()
        print(f"Seeded {len(data)} restaurants into the database.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
