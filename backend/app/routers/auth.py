from fastapi import APIRouter, HTTPException, status

from app.auth import CurrentUser, DbSession, create_access_token, get_user_by_email, hash_password, verify_password
from app.models import User
from app.schemas import ProfileUpdate, Token, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: DbSession):
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
        target_role=payload.target_role,
        experience_level=payload.experience_level,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.email)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: DbSession):
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.email)
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser):
    return UserOut.model_validate(user)


@router.patch("/me", response_model=UserOut)
def update_me(payload: ProfileUpdate, user: CurrentUser, db: DbSession):
    if payload.full_name is not None:
        user.full_name = payload.full_name.strip()
    if payload.target_role is not None:
        user.target_role = payload.target_role
    if payload.experience_level is not None:
        user.experience_level = payload.experience_level
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)
