# Auth endpoints

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import SessionLocal
from schemas.user import UserCreate, UserLogin, UserRead
from schemas.token import Token
from services.auth_service import create_user, login_user, get_user_by_username
from utils.security import decode_access_token
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db():
    async with SessionLocal() as session:
        yield session


async def get_current_user_dependency(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    username = decode_access_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user = await db.run_sync(lambda s: get_user_by_username(s, username))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    return await db.run_sync(lambda s: get_user_by_username(s, username))


@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = await create_user(db, user)
    return new_user


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_user(db, user_login)


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: Annotated[UserRead, Depends(get_current_user_dependency)],
):
    return current_user
