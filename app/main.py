"""
Main application entry point for the Hotel Booking System.

This module configures the FastAPI application, middleware, and routes for
all of the services that make up the hotel booking system. It also seeds a
default superuser on startup and ensures that all SQLModel tables are
registered before the database is initialized.

Routers are grouped by domain: authentication, user management, rooms,
bookings, payments, admin operations, chat, AI recommendations, property
management, property extras (amenities, images, experiences), availability
quoting, and staff operations. New routers can be added here without
affecting existing functionality.

The default superuser is created if one does not already exist. This
superuser can be used to perform administrative tasks via the API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import init_db, engine
from app.core.logger import logger
from app.models.user import User
from app.utils.security import hash_password
from app.utils.enums import UserRole

# Import all models so SQLModel registers them with the metadata. Without
# this import, SQLModel will not be aware of tables defined in other
# modules when `SQLModel.metadata.create_all()` is called.
import app.models  # noqa: F401

# Import routers from their respective modules. Grouping routers this way
# keeps the API organized and makes it easy to add new functionality.
from app.routers import (
    auth,
    users,
    rooms,
    bookings,
    payments,
    admin,
    chat,
    ai,
    properties,
    property_extras,
    availability,
    staff,
    organizations,
    analytics,
    search,
    subscriptions,
    public,
    experiences,
    customers,
    inventory,
)


def create_app() -> FastAPI:
    """Factory function to create and configure the FastAPI application."""
    application = FastAPI(title=settings.PROJECT_NAME)

    # Configure CORS settings from the environment. Multiple origins can be
    # specified as a comma-separated list in the CORS_ORIGINS setting.
    # For development, allow common frontend ports
    cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    # Add development ports if not already included
    dev_origins = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:5173"]
    for origin in dev_origins:
        if origin not in cors_origins:
            cors_origins.append(origin)
    
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers for each domain of the application. The order of
    # inclusion does not matter, but logically grouping them can help with
    # readability when viewing the auto-generated API docs.
    application.include_router(public.router)        # Public/marketing pages first
    application.include_router(auth.router)
    application.include_router(organizations.router)  # Multi-tenancy first
    application.include_router(subscriptions.router) # Subscription management
    application.include_router(search.router)         # Search & availability
    application.include_router(analytics.router)      # Advanced analytics
    application.include_router(users.router)
    application.include_router(customers.router)      # Customer features
    application.include_router(rooms.router)
    application.include_router(bookings.router)
    application.include_router(payments.router)
    application.include_router(admin.router)
    application.include_router(chat.router)
    application.include_router(ai.router)
    application.include_router(properties.router)
    application.include_router(property_extras.router)
    application.include_router(experiences.router)    # Experience management
    application.include_router(availability.router)
    application.include_router(inventory.router)      # Inventory management
    application.include_router(staff.router)

    @application.on_event("startup")
    def on_startup() -> None:
        """Initialize the database and seed a default superuser on startup."""
        # Create database tables. `app.models` has been imported above so all
        # tables are registered with SQLModel's metadata.
        init_db()

        # Create a default superuser if one does not already exist. Using a
        # context-managed session ensures the connection is closed properly.
        with Session(engine) as session:
            existing_user = session.exec(
                select(User).where(User.email == settings.SUPERUSER_EMAIL)
            ).first()

            if not existing_user:
                admin_user = User(
                    email=settings.SUPERUSER_EMAIL,
                    password_hash=hash_password(settings.SUPERUSER_PASSWORD),
                    full_name="Administrator",
                    role=UserRole.ADMIN,
                    is_active=True,
                    phone="0123456789",
                )
                session.add(admin_user)
                session.commit()
                logger.info(
                    f"✅ Created default superuser: {settings.SUPERUSER_EMAIL}"
                )
            else:
                logger.info("✅ Superuser already exists, skip seeding.")

        logger.info("✅ App started and DB initialized")

    return application


# Create the FastAPI app instance. This will be picked up by ASGI servers
# (e.g., Uvicorn, Gunicorn) when running the application.
app = create_app()