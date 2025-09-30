from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import User
from app.schemas.token import Token
from app.utils.security import authenticate_user,hash_password
from app.utils.jwt import create_access_token,create_refresh_token
from app.utils.dependencies import SessionDep
from app.schemas.user import UserCreate,UserRead


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login(
    session: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    # 1. Tìm user theo username hoặc email
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username/email or password",
        )

    # 3. Check is_active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user. Please contact admin.",
        )

    # 4. Nếu ok → cấp token
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/register", response_model=UserRead)
def register(
    session: SessionDep,
    payload: UserCreate,
):
    # 1. Check email đã tồn tại chưa
    existing_user = session.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )


    # 3. Tạo user mới
    new_user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),  # dùng hash
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # 4. Trả về thông tin user
    return new_user


