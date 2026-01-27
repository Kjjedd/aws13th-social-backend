from fastapi import APIRouter, HTTPException, status
from schemas.session import SessionCreate, SessionResponse
from service.session import authenticate_user, AuthenticationFailedError

router = APIRouter(
    tags=["Sessions"]
)

@router.post("/sessions", response_model=SessionResponse)
def login(session: SessionCreate):
    try:
        return authenticate_user(session)
    except AuthenticationFailedError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": "error",
                "error": {
                    "code": "AUTHENTICATION_FAILED",
                    "message": "이메일 또는 비밀번호가 올바르지 않습니다.",
                    "details": {
                        "reason": "INVALID_CREDENTIALS"
                    }
                }
            }
        )