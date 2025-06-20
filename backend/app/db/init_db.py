# backend/app/db/init_db.py
import logging
from sqlalchemy.orm import Session
from app.db.session import engine, Base, SessionLocal
from app.core.config import settings
from app.schemas.user import UserCreate
from app.services import user_service

# Create a logger for this module
logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    Initialize the database with required tables and initial data.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create initial admin user if doesn't exist
    db = SessionLocal()
    try:
        create_initial_users(db)
    except Exception as e:
        logger.error(f"Error creating initial users: {e}")
    finally:
        db.close()

def create_initial_users(db: Session) -> None:
    """
    Create initial admin user if it doesn't exist.
    """
    # Check if admin user exists
    admin_email = "admin@cyberedpro.com"
    user = user_service.get_by_email(db, email=admin_email)

    if not user:
        # Create admin user
        admin_user = UserCreate(
            email=admin_email,
            password="Admin123!",  # Change in production!
            first_name="Admin",
            last_name="User",
            role="admin",
            is_active=True
        )
        user_service.create(db, obj_in=admin_user)
        logger.info("Admin user created")