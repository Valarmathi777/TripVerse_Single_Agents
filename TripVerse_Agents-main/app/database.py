import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "trips.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination TEXT NOT NULL,
                days INTEGER NOT NULL,
                interests TEXT,
                plan TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Add must_include column if it doesn't exist
        try:
            conn.execute("ALTER TABLE trips ADD COLUMN must_include TEXT")
        except sqlite3.OperationalError:
            pass
        conn.commit()
    finally:
        conn.close()

def save_trip(destination: str, days: int, interests: str, must_include: str, plan: dict) -> int:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO trips (destination, days, interests, must_include, plan) VALUES (?, ?, ?, ?, ?)",
            (destination, days, interests, must_include, json.dumps(plan))
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_all_trips():
    conn = get_db_connection()
    try:
        rows = conn.execute("SELECT * ORDER BY created_at DESC" if False else "SELECT id, destination, days, interests, plan, created_at, (CASE WHEN EXISTS (SELECT 1 FROM pragma_table_info('trips') WHERE name='must_include') THEN must_include ELSE '' END) as must_include FROM trips ORDER BY created_at DESC").fetchall()
        # Actually since we alter table in init_db, it will definitely have must_include, but let's query safely
        rows = conn.execute("SELECT * FROM trips ORDER BY created_at DESC").fetchall()
        trips = []
        for row in rows:
            try:
                plan_data = json.loads(row["plan"])
            except Exception:
                plan_data = row["plan"]
            
            # Safely get must_include field
            must_include_val = ""
            if "must_include" in row.keys():
                must_include_val = row["must_include"] or ""

            trips.append({
                "id": row["id"],
                "destination": row["destination"],
                "days": row["days"],
                "interests": row["interests"],
                "must_include": must_include_val,
                "plan": plan_data,
                "created_at": row["created_at"]
            })
        return trips
    finally:
        conn.close()

def delete_trip(trip_id: int) -> bool:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def update_trip(trip_id: int, destination: str, days: int, interests: str, must_include: str, plan: dict) -> bool:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE trips SET destination = ?, days = ?, interests = ?, must_include = ?, plan = ? WHERE id = ?",
            (destination, days, interests, must_include, json.dumps(plan), trip_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
