from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
from utils.data import load_json
from fastapi import Request, HTTPException, status

import os

# .env 로드
load_dotenv()

# 환경 변수
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_SECONDS = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 3600))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# 비밀번호 관련
# =========================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# =========================
# JWT 관련
# =========================

def create_access_token(user_id: str) -> str:
    """
    JWT Access Token 생성

    subject 예:
    {
        "user_id": "user_1"
    }
    """
    expire = datetime.now(timezone.utc) + timedelta(
        seconds=ACCESS_TOKEN_EXPIRE_SECONDS
    )

    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    JWT 검증 및 payload 반환
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def _auth_error(reason: str):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "status": "error",
            "error": {
                "code": "AUTH_REQUIRED",
                "message": "인증이 필요합니다.",
                "details": {
                    "reason": reason
                }
            }
        }
    )

def get_current_user(request: Request) -> Dict[str, Any]:
    auth_header = request.headers.get("Authorization")

    # 1. 헤더 존재 + 형식 확인
    if not auth_header or not auth_header.startswith("Bearer "):
        raise _auth_error("MISSING_OR_INVALID_TOKEN")

    token = auth_header.split(" ")[1]

    # 2. JWT 검증
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise _auth_error("INVALID_TOKEN")

    except JWTError:
        raise _auth_error("INVALID_OR_EXPIRED_TOKEN")

    # 3. 실제 사용자 조회
    users = load_json("users.json")
    user = next((u for u in users if u["id"] == user_id), None)

    if not user:
        raise _auth_error("USER_NOT_FOUND")

    return user