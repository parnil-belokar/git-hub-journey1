from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import urllib.parse
import os

project_id = "vzvyjryvryggevkuumhm"
password = urllib.parse.quote_plus("Sushant@2026")
db_host = "aws-1-ap-northeast-2.pooler.supabase.com"

SQLALCHEMY_DATABASE_URL = f"postgresql://postgres.{project_id}:{password}@{db_host}:6543/postgres"

try:
    print("Testing connection...")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    connection = engine.connect()
    print("Connection successful!")
    connection.close()
except Exception as e:
    print(f"Connection failed: {e}")
