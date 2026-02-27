from database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        print("Migrating database...")
        try:
            conn.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS department VARCHAR;"))
            conn.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS voice_url VARCHAR;"))
            conn.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS votes INTEGER DEFAULT 0;"))
            conn.commit()
            print("Migration successful!")
        except Exception as e:
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
