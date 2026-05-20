from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.college_schema import (
    TokenResponse,
    UserLoginSchema,
    UserRegisterSchema,
    UserResponse,
)
from services.auth_service import (
    create_token,
    get_current_user,
    login_user_service,
    register_user_service,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user: UserRegisterSchema, db: Session = Depends(get_db)):
    result = register_user_service(user, db)

    if result is None:
        raise HTTPException(status_code=409, detail="User email already exists")

    if result == "invalid_role":
        raise HTTPException(status_code=400, detail="Role must be admin or student")

    return result


@router.post("/login", response_model=TokenResponse)
def login_user(user: UserLoginSchema, db: Session = Depends(get_db)):
    db_user = login_user_service(user, db)

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_token(db_user)
    return {"access_token": access_token, "token_type": "bearer", "user": db_user}


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user
