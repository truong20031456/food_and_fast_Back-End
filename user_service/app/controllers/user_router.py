from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserListResponse, user
from app.services.user_service import (
    create_user,
    get_user,
    update_user,
    soft_delete_user,
    list_users,
)
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/users/google", response_model=user)
async def google_login(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Gọi hàm tạo user từ dịch vụ
    try:
        db_user = await create_user(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return db_user


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Đăng ký user không cần xác thực
    try:
        user = await create_user(db, user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserRead)
async def get_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user_endpoint(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    user = await update_user(db, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    success = await soft_delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or already deleted")
    return None


@router.get("/", response_model=UserListResponse)
async def list_users_endpoint(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    total, users = await list_users(db, limit=limit, offset=offset)
    return UserListResponse(total=total, users=users)
