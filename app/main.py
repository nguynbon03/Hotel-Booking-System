from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from app.core.config import settings
from app.core.database import init_db, engine
from app.core.logger import logger
from app.models.user import User
from app.utils.security import hash_password
from app.routers import auth, users, rooms, bookings, payments, admin, chat, ai
from app.utils.enums import UserRole

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(rooms.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(admin.router)
app.include_router(chat.router)
app.include_router(ai.router)


@app.on_event("startup")
def on_startup():
    init_db()
    with Session(engine) as session:
        existing = session.exec(
            select(User).where(User.email == settings.SUPERUSER_EMAIL)
        ).first()

        if not existing:
            admin_user = User(
                email=settings.SUPERUSER_EMAIL,
                password_hash=hash_password(settings.SUPERUSER_PASSWORD),
                full_name="Administrator",
                role=UserRole.ADMIN,   # ✅ Enum
                is_active=True,
                phone="0123456789",
            )
            session.add(admin_user)
            session.commit()
            logger.info(f"✅ Created default superuser: {settings.SUPERUSER_EMAIL}")
        else:
            logger.info("✅ Superuser already exists, skip seeding.")

    logger.info("✅ App started and DB initialized")
