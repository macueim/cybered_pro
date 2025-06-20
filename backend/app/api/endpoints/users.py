# backend/app/api/endpoints/users.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user, get_current_active_superuser, get_db
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserInDB
from app.services import user_service

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
        *,
        db: Session = Depends(get_db),
        user_in: UserCreate
) -> Any:
    """
    Register a new user.
    """
    user = user_service.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )
    user = user_service.create(db, obj_in=user_in)
    return user

# backend/app/api/endpoints/users.py
@router.post("/login", response_model=dict)
def login(
        *,
        db: Session = Depends(get_db),
        login_data: dict  # Change this to accept a request body
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    username = login_data.get("username")
    password = login_data.get("password")

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username and password are required",
        )

    user = user_service.authenticate(db, email=username, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user_service.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    return {
        "access_token": user_service.create_access_token(user.id),
        "token_type": "bearer",
    }
@router.get("/me", response_model=UserResponse)
def read_user_me(
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user profile.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_me(
        *,
        db: Session = Depends(get_db),
        user_in: UserUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update own user profile.
    """
    user = user_service.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/", response_model=List[UserResponse])
def read_users(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve all users. Admin only.
    """
    users = user_service.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(
        user_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id. Admin can get any user, users can only get themselves.
    """
    user = user_service.get(db, id=user_id)
    if user == current_user:
        return user
    if not user_service.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        user_in: UserUpdate,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a user. Admin only.
    """
    user = user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    user = user_service.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(
        *,
        db: Session = Depends(get_db),
        user_id: int,
        current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Delete a user. Admin only.
    """
    user = user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    user = user_service.delete(db, id=user_id)
    return user