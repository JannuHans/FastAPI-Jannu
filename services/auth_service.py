import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User
from schemas.college_schema import UserLoginSchema, UserRegisterSchema


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "my-secret-key")
TOKEN_EXPIRE_SECONDS = 60 * 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def make_password_hash(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(password: str, hashed_password: str):
    return make_password_hash(password) == hashed_password


def encode_base64(data: bytes):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def decode_base64(data: str):
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_token(user: User):
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "user_id": user.id,
        "role": user.role,
        "exp": int(time.time()) + TOKEN_EXPIRE_SECONDS,
    }

    encoded_header = encode_base64(json.dumps(header).encode())
    encoded_payload = encode_base64(json.dumps(payload).encode())
    unsigned_token = f"{encoded_header}.{encoded_payload}"

    signature = hmac.new(
        SECRET_KEY.encode(),
        unsigned_token.encode(),
        hashlib.sha256,
    ).digest()

    return f"{unsigned_token}.{encode_base64(signature)}"


def read_token(token: str):
    try:
        encoded_header, encoded_payload, signature = token.split(".")
        unsigned_token = f"{encoded_header}.{encoded_payload}"

        correct_signature = hmac.new(
            SECRET_KEY.encode(),
            unsigned_token.encode(),
            hashlib.sha256,
        ).digest()

        if encode_base64(correct_signature) != signature:
            return None

        payload = json.loads(decode_base64(encoded_payload))
        if payload["exp"] < int(time.time()):
            return None

        return payload
    except Exception:
        return None


def register_user_service(user: UserRegisterSchema, db: Session):
    if user.role not in ["admin", "student"]:
        return "invalid_role"

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        return None

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=make_password_hash(user.password),
        role=user.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user_service(user: UserLoginSchema, db: Session):
    db_user = db.query(User).filter(User.email == user.email).first()

    if db_user is None:
        return None

    if not check_password(user.password, db_user.hashed_password):
        return None

    return db_user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = read_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = db.query(User).filter(User.id == payload["user_id"]).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access this route",
        )

    return current_user
