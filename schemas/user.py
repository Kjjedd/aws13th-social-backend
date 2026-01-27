import re
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional

# 공통 응답 구조를 위한 베이스 모델
class ResponseBase(BaseModel):
    status: str = "success"

# 회원가입 요청 규격
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    nickname: str = Field(..., min_length=2, description="2자 이상의 닉네임")
    profile_image_url: Optional[str] = None

    @validator("password")
    def validate_password(cls, value: str) -> str:
        """
        비밀번호 보안 정책:
        - 최소 8자
        - 대문자 1개 이상
        - 소문자 1개 이상
        - 숫자 1개 이상
        - 특수문자 1개 이상
        """
        if len(value) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")

        if not re.search(r"[A-Z]", value):
            raise ValueError("비밀번호에 대문자가 최소 1개 포함되어야 합니다.")

        if not re.search(r"[a-z]", value):
            raise ValueError("비밀번호에 소문자가 최소 1개 포함되어야 합니다.")

        if not re.search(r"[0-9]", value):
            raise ValueError("비밀번호에 숫자가 최소 1개 포함되어야 합니다.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("비밀번호에 특수문자가 최소 1개 포함되어야 합니다.")

        return value

# 회원 정보 응답 규격
class UserInfo(BaseModel):
    id: str
    email: EmailStr
    nickname: str
    profile_image_url: Optional[str]
    created_at: datetime

# 최종 회원가입 응답 구조
class UserRegistrationResponse(ResponseBase):
    data: UserInfo

class MyProfileResponse(ResponseBase):
    data: UserInfo