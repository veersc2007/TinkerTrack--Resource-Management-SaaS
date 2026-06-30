from app.database import SessionLocal
# Import ALL models
from app.models.user import User
from app.models.resource import Resource
from app.models.reservation import Reservation

# -----------------------------
# CHANGE THIS EMAIL
# -----------------------------
ADMIN_EMAIL = "user@gmail.com"
# Example:
# ADMIN_EMAIL = "aditya@gmail.com"

db = SessionLocal()

try:
    user = db.query(User).filter(User.email == ADMIN_EMAIL).first()

    if not user:
        print(f"❌ User with email '{ADMIN_EMAIL}' not found.")

    else:
        user.role = "admin"
        db.commit()
        db.refresh(user)

        print("===================================")
        print("✅ User promoted successfully!")
        print(f"Name : {user.name}")
        print(f"Email: {user.email}")
        print(f"Role : {user.role}")
        print("===================================")

finally:
    db.close()
