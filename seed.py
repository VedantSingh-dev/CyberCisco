import os
import sys
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Ensure project root is in the python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.database.dbConfig import Base, SessionLocal, engine

# 1. Import ALL models so SQLAlchemy can resolve relationship mapping strings
from src.modals.courses_models import Course
from src.modals.payments_models import Payment  # Fixes 'Payment' location error
from src.modals.user_models import User

# Configure passlib bcrypt context directly inside the script
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def seed_admin_user():
    # Ensure database tables are created after all models are loaded
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    admin_email = "vedants.2024@upsifs.ac.in"
    admin_name = "vedant singh"
    raw_password = "134@abc"

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == admin_email).first()

        if existing_user:
            print(f"⚠️ User with email '{admin_email}' already exists.")

            # Promote to ADMIN if not already
            if getattr(existing_user, "role", None) != "ADMIN":
                existing_user.role = "ADMIN"
                db.commit()
                print("🔄 Existing user updated to role 'ADMIN'.")
            return

        # Hash password and create admin record
        hashed_pwd = hash_password(raw_password)

        admin_user = User(
            full_name=admin_name,
            email=admin_email,
            hashed_password=hashed_pwd,
            role="ADMIN",
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("✅ Admin user seeded successfully!")
        print(f"   Name:  {admin_user.full_name}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role:  {admin_user.role}")

    except Exception as e:
        db.rollback()
        print(f"❌ Failed to seed admin user: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin_user()