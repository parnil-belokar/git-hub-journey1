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
            con.execute(text("ALTER TABLE complaints ADD COLUMN estimated_completion_time VARCHAR NULL;"))
            print("estimated_completion_time added")
        except Exception as e: print(e)

if __name__ == "__main__":
    run()
