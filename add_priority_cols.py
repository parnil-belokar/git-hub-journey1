import urllib.parse
from sqlalchemy import create_engine, text

project_id = "vzvyjryvryggevkuumhm"
password = urllib.parse.quote_plus("Sushant@2026")
db_host = "aws-1-ap-northeast-2.pooler.supabase.com"
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres.{project_id}:{password}@{db_host}:6543/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def run():
    with engine.begin() as con:
        # Add columns to complaints
        for col, default in [("community_yes_ratio", "0.5"), ("critical_area_weight", "0.3"), ("department_urgency_index", "0.5"), ("priority_score", "0.0")]:
            try: con.execute(text(f"ALTER TABLE complaints ADD COLUMN {col} FLOAT DEFAULT {default};"))
            except: pass
            
        # PostGIS extension
        try:
            con.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        except Exception as e: print("PostGIS:", e)

        # Department Urgency Matrix
        try:
            con.execute(text("""
            CREATE TABLE IF NOT EXISTS department_urgency_matrix (
                id SERIAL PRIMARY KEY,
                department VARCHAR,
                issue_type VARCHAR,
                urgency_index FLOAT,
                UNIQUE(department, issue_type)
            );
            """))
            con.execute(text("""
            INSERT INTO department_urgency_matrix (department, issue_type, urgency_index) VALUES 
            ('Water Supply', 'Water Leakage', 0.6),
            ('Water Supply', 'Low Water Pressure', 0.4),
            ('Water Supply', 'Broken Pipeline', 1.0),
            ('Water Supply', 'No Water Supply', 0.8),
            ('Electricity', 'Exposed Wire', 1.0),
            ('Electricity', 'Power Failure', 0.9),
            ('Electricity', 'Transformer Issue', 0.9),
            ('Road & Infrastructure', 'Pothole', 0.6),
            ('Road & Infrastructure', 'Road Crack', 0.4),
            ('Road & Infrastructure', 'Blocked Drain', 0.8),
            ('Road & Infrastructure', 'Broken Footpath', 0.5),
            ('Waste Management', 'Garbage Heap', 0.5),
            ('Waste Management', 'Stray Animal Issue', 0.7),
            ('Waste Management', 'Drainage Block', 0.8),
            ('Streetlight Maintenance', 'Light Not Working', 0.4),
            ('Streetlight Maintenance', 'Continuous Dimm', 0.3),
            ('Sanitation', 'Clogged Sewer', 0.9),
            ('Sanitation', 'Public Toilet Issue', 0.7)
            ON CONFLICT DO NOTHING;
            """))
        except Exception as e: print("Matrix:", e)

        # Critical Places setup
        try:
            con.execute(text("""
            CREATE TABLE IF NOT EXISTS critical_places (
                id SERIAL PRIMARY KEY,
                name VARCHAR,
                place_type VARCHAR,
                location geography(POINT, 4326),
                weight FLOAT
            );
            """))
            # Dummy insertions
            con.execute(text("""
            INSERT INTO critical_places (name, place_type, location, weight)
            SELECT 'City Hospital', 'Hospital', ST_SetSRID(ST_MakePoint(77.2090, 28.6139), 4326)::geography, 1.0
            WHERE NOT EXISTS (SELECT 1 FROM critical_places);
            """))
        except Exception as e: print("Places:", e)

        print("Schemas updated!")

if __name__ == "__main__":
    run()
