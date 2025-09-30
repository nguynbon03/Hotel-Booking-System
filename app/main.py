from fastapi import FastAPI

from app.core.database import init_db
from app.routers.auth import router as auth_router
from app.routers.user import router as users_router
from app.services.user_service import init_super_user



app = FastAPI(title="fastapi-user-api")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    init_super_user()


app.include_router(auth_router)
app.include_router(users_router)
