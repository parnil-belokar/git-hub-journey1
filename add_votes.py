import urllib.parse
from sqlalchemy import create_engine, text

project_id = "vzvyjryvryggevkuumhm"
password = urllib.parse.quote_plus("Sushant@2026")
db_host = "aws-1-ap-northeast-2.pooler.supabase.com"
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres.{project_id}:{password}@{db_host}:6543/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def run():
    with engine.begin() as con:
        try:
            con.execute(text("ALTER TABLE complaints ADD COLUMN yes_votes INTEGER DEFAULT 0;"))
            print("yes_votes added")
        except Exception as e: print(e)
        try:
            con.execute(text("ALTER TABLE complaints ADD COLUMN no_votes INTEGER DEFAULT 0;"))
            print("no_votes added")
        except Exception as e: print(e)
        try:
            con.execute(text("ALTER TABLE complaints ADD COLUMN idk_votes INTEGER DEFAULT 0;"))
            print("idk_votes added")
        except Exception as e: print(e)
        try:
            con.execute(text("""
            CREATE TABLE IF NOT EXISTS votes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                complaint_id INTEGER REFERENCES complaints(id),
                vote_type VARCHAR(10),
                UNIQUE(user_id, complaint_id)
            );
            """))
            print("votes table created")
        except Exception as e: print(e)

if __name__ == "__main__":
    run()
