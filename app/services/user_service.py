from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate,AdminUpdate
from app.utils.security import hash_password

from sqlmodel import Session, select
from app.models.user import User
from app.core.database import engine
from app.utils.security import hash_password
from app.core.config import settings


def init_super_user():
    """Tạo superuser mặc định nếu chưa có"""
    with Session(engine) as session:
        statement = select(User).where(User.email == settings.SUPERUSER_EMAIL)
        user = session.exec(statement).first()

        if not user:
            super_user = User(
                email=settings.SUPERUSER_EMAIL,
                username="admin",  # bạn có thể lấy từ env nếu muốn
                hashed_password=hash_password(settings.SUPERUSER_PASSWORD),
                is_superuser=True
            )
            session.add(super_user)
            session.commit()
            print(f"[INIT] Superuser created: {settings.SUPERUSER_EMAIL}")
        else:
            print(f"[INIT] Superuser already exists: {user.email}")



def get_user_by_id(session: Session, user_id: UUID) -> Optional[User]:
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(session: Session, data: UserCreate) -> User:
    if get_user_by_username(session, data.username) or get_user_by_email(session, data.email):
        raise ValueError("Username or email already exists")
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(session: Session, user: User, data:UserUpdate ) -> User:
    update_data = data.dict(exclude_unset=True)  # chỉ lấy field được gửi lên

    # Nếu có password thì hash lại
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user
def update_superuser(session: Session, user: User, data:AdminUpdate ) -> User:
    update_data = data.dict(exclude_unset=True)  # chỉ lấy field được gửi lên

    # Nếu có password thì hash lại
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user



def delete_user(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()


def list_users(
    session: Session,
    *,
    offset: int = 0,
    limit: int = 50,
) -> list[User]:
    statement = select(User).offset(offset).limit(limit)
    return list(session.exec(statement).all())
