from pydantic import BaseModel, EmailStr, Field


class SessionCreate(BaseModel):
    email: EmailStr = Field(..., description="로그인 이메일")
    password: str = Field(..., min_length=8, description="비밀번호")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(
        ...,
        description="토큰 만료 시간 (초)",
        json_schema_extra={
            "example": 3600
        }
    )

class SessionResponse(BaseModel):
    status: str
    data: TokenResponse