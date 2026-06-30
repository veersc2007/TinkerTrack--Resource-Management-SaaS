from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Body


from app.database import get_db

from app.models.user import User

from app.schemas.auth import (
    RegisterSchema,
    LoginSchema,
    Token
)

from app.schemas.user import UserResponse

from app.auth.security import (
    hash_password,
    verify_password
)

from app.auth.jwt_handler import create_access_token

from app.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["🔐 Authentication"]
)


# ----------------------------------------------------
# REGISTER
# ----------------------------------------------------

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    user: RegisterSchema,
    db: Session = Depends(get_db)
):

    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role="student"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ----------------------------------------------------
# LOGIN
# ----------------------------------------------------

@router.post(
    "/login",
    response_model=Token
)
def login(
    user: LoginSchema,
    db: Session = Depends(get_db)
):

    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user.password,
        existing.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {
            "sub": str(existing.id)
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ----------------------------------------------------
# CURRENT USER
# ----------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

    return {"message": "User created successfully"}


@router.post("/login")
def login(
    user: LoginSchema = Body(
        ...,
        example={
            "email": "student@iit.edu",
            "password": "secure123"
        }
    ),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({
        "user_id": db_user.id,
        "role": db_user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
