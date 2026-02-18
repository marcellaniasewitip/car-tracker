import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="inspection_logs.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            plate_number TEXT,
            mileage TEXT,
            engine_number TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def save_entry(self, plate, mileage, engine):
        query = "INSERT INTO inspections (timestamp, plate_number, mileage, engine_number) VALUES (?, ?, ?, ?)"
        self.conn.execute(query, (datetime.now(), plate, mileage, engine))
        self.conn.commit()
        print(f"\n[DATABASE] Data saved for Plate: {plate}")