
from database import SessionLocal
import models

db = SessionLocal()
users = db.query(models.User).all()
print(f"Total Users: {len(users)}")
for u in users:
    print(f"ID: {u.id}, Phone: {u.phone_number}, Name: {u.name}")
db.close()
