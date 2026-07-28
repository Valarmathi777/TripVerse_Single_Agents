import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "stays.db")

def init_db(db_path=DB_PATH):
    """Initializes the SQLite database and creates the stays table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            checkin TEXT,
            checkout TEXT,
            guests INTEGER,
            budget TEXT,
            travel_style TEXT,
            accommodation TEXT,
            requirements TEXT,
            recommended_area TEXT,
            area_reason TEXT,
            hotels_json TEXT,
            estimated_total_cost TEXT,
            best_choice TEXT,
            travel_tips_json TEXT,
            notes TEXT DEFAULT '',
            rating INTEGER DEFAULT 0,
            is_bookmarked INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_stay(request_data: dict, response_data: dict, db_path=DB_PATH) -> int:
    """Saves the requested parameters and the generated stay plan to the database."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    recommended_area = response_data.get("recommended_area", "")
    area_reason = response_data.get("area_reason", "")
    hotels = response_data.get("hotels", [])
    estimated_total_cost = response_data.get("estimated_total_cost", "")
    best_choice = response_data.get("best_choice", "")
    travel_tips = response_data.get("travel_tips", [])
    
    cursor.execute("""
        INSERT INTO stays (
            destination, checkin, checkout, guests, budget, travel_style, accommodation, requirements,
            recommended_area, area_reason, hotels_json, estimated_total_cost, best_choice, travel_tips_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request_data.get("destination", ""),
        request_data.get("checkin", ""),
        request_data.get("checkout", ""),
        int(request_data.get("guests", 1)),
        request_data.get("budget", ""),
        request_data.get("travel_style", ""),
        request_data.get("accommodation", ""),
        request_data.get("requirements", ""),
        recommended_area,
        area_reason,
        json.dumps(hotels),
        estimated_total_cost,
        best_choice,
        json.dumps(travel_tips)
    ))
    
    stay_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return stay_id

def get_all_stays(db_path=DB_PATH, search_query: str = None, filter_bookmarked: bool = False):
    """Fetches all stays from history, with optional search and bookmark filters."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM stays WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND destination LIKE ?"
        params.append(f"%{search_query}%")
        
    if filter_bookmarked:
        query += " AND is_bookmarked = 1"
        
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    results = []
    for row in rows:
        item = dict(row)
        try:
            item["hotels"] = json.loads(item["hotels_json"])
        except:
            item["hotels"] = []
        try:
            item["travel_tips"] = json.loads(item["travel_tips_json"])
        except:
            item["travel_tips"] = []
        results.append(item)
        
    conn.close()
    return results

def get_stay_by_id(stay_id: int, db_path=DB_PATH):
    """Fetches details of a specific stay by its ID."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM stays WHERE id = ?", (stay_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
        
    item = dict(row)
    try:
        item["hotels"] = json.loads(item["hotels_json"])
    except:
        item["hotels"] = []
    try:
        item["travel_tips"] = json.loads(item["travel_tips_json"])
    except:
        item["travel_tips"] = []
        
    conn.close()
    return item

def delete_stay(stay_id: int, db_path=DB_PATH) -> bool:
    """Deletes a stay from history."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM stays WHERE id = ?", (stay_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def toggle_bookmark(stay_id: int, db_path=DB_PATH) -> dict:
    """Toggles bookmark status (0 -> 1 or 1 -> 0) and returns new state."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT is_bookmarked FROM stays WHERE id = ?", (stay_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"status": "error", "message": "Stay not found"}
        
    new_status = 1 if row[0] == 0 else 0
    cursor.execute("UPDATE stays SET is_bookmarked = ? WHERE id = ?", (new_status, stay_id))
    conn.commit()
    conn.close()
    return {"status": "success", "is_bookmarked": new_status}

def update_notes(stay_id: int, notes: str, db_path=DB_PATH) -> bool:
    """Updates user personal notes on a stay."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE stays SET notes = ? WHERE id = ?", (notes, stay_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def update_rating(stay_id: int, rating: int, db_path=DB_PATH) -> bool:
    """Updates user rating (0 to 5)."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("UPDATE stays SET rating = ? WHERE id = ?", (rating, stay_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_stats(db_path=DB_PATH) -> dict:
    """Generates simple planning analytics dashboard statistics."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM stays")
    total_stays = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM stays WHERE is_bookmarked = 1")
    total_bookmarked = cursor.fetchone()[0]
    
    cursor.execute("SELECT destination, COUNT(destination) as count FROM stays GROUP BY destination ORDER BY count DESC LIMIT 3")
    popular_destinations = [{"destination": r[0], "count": r[1]} for r in cursor.fetchall()]
    
    cursor.execute("SELECT AVG(rating) FROM stays WHERE rating > 0")
    avg_rating = cursor.fetchone()[0]
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    
    conn.close()
    return {
        "total_stays": total_stays,
        "total_bookmarked": total_bookmarked,
        "popular_destinations": popular_destinations,
        "average_rating": avg_rating
    }
