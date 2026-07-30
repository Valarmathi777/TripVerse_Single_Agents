from database import SessionLocal, RestaurantDB, create_tables

def load_restaurants():
    create_tables()
    db = SessionLocal()
    try:
        rows = db.query(RestaurantDB).all()
        return [
            {
                "name": r.name,
                "location": r.location,
                "cuisine": r.cuisine,
                "budget": r.budget,
                "type": r.type,
                "rating": r.rating,
                "meal_time": r.meal_time,
                "address": r.address,
                "description": r.description,
            }
            for r in rows
        ]
    finally:
        db.close()

restaurants = load_restaurants()
