from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.user import (
    UserCreate,
    UserRead,
    UserUpdate,
    UserListResponse,
    UserLogin,
)
from app.services.user_service import (
    create_user,
    get_user,
    update_user,
    soft_delete_user,
    list_users,
    authenticate_user,
)
from app.dependencies import get_current_user_id
from app.exceptions import (
    UserServiceException,
    UserNotFoundError,
    DuplicateUserError,
    UserAuthorizationError,
    DatabaseError,
    CacheError,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/login", response_model=dict)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    """Traditional login with username/email and password"""
    try:
        user = await authenticate_user(db, user_in.username_or_email, user_in.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Generate JWT token
        from app.utils.jwt_helper import create_access_token

        token = create_access_token(data={"sub": user.id})
        return {"access_token": token, "token_type": "bearer"}
    except UserServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/google", response_model=UserRead)
async def google_login(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Create user from Google OAuth data
    try:
        db_user = await create_user(db, user_in)
        return db_user
    except DuplicateUserError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    except UserServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Register user without authentication
    try:
        user = await create_user(db, user_in)
        return user
    except DuplicateUserError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    except UserServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserRead)
async def get_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    # Authorization: Users can only access their own data
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied")

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
    # Authorization: Users can only update their own data
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        user = await update_user(db, user_id, user_in)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except DuplicateUserError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    except UserServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    # Authorization: Users can only delete their own account
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied")

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
    # Validate pagination parameters
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    if offset < 0:
        raise HTTPException(status_code=400, detail="Offset must be non-negative")

    total, users = await list_users(db, limit=limit, offset=offset)
    return UserListResponse(total=total, users=users)


@router.get("/me", response_model=UserRead)
async def get_current_user_endpoint(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get current user profile"""
    user = await get_user(db, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
