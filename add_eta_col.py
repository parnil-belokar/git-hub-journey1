import urllib.parse
from sqlalchemy import create_engine, text

project_id = ""
password = 
db_host = ""
SQLALCHEMY_DATABASE_URL = f""

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def run():
    with engine.begin() as con:
        try:
            con.execute(text("ALTER TABLE complaints ADD COLUMN estimated_completion_time VARCHAR NULL;"))
            print("estimated_completion_time added")
        except Exception as e: print(e)

if __name__ == "__main__":
    run()
