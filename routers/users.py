from fastapi import APIRouter, HTTPException, status, Request, Depends
from core.limiter import limiter
from schemas.user import UserCreate, UserRegistrationResponse, MyProfileResponse
from service.user import create_user, DuplicateResourceError, UserCreateFailedError
from utils.auth import get_current_user

router = APIRouter(
    prefix="/users", tags=["Users"]
)

@router.post("/",
             response_model=UserRegistrationResponse,
             status_code=status.HTTP_201_CREATED
             )
# 동일 IP당 1분에 최대 5번 회원가입 시도 제한
@limiter.limit("5/minute")
def register_user(
        request: Request,
        user: UserCreate):
    try:
        # 서비스 계층에서 유저 생성 로직 수행
        new_user = create_user(user)

        return {
            "status": "success",
            "data": {
                "id": new_user["id"],
                "email": new_user["email"],
                "nickname": new_user["nickname"],
                "profile_image_url": new_user["profile_image_url"],
                "created_at": new_user["created_at"],
            }
        }
    except DuplicateResourceError as e:
        message_map = {
            "email": "이미 사용 중인 이메일 입니다.",
            "nickname": "이미 사용 중인 닉네임 입니다."
        }
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "status": "error",
                "error": {
                    "code": "DUPLICATE_RESOURCE",
                    "message": message_map.get(e.field, "중복된 리소스 입니다."),
                    "details": {
                        "field": e.field
                    }
                }
            }
        )
    except UserCreateFailedError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "회원가입 처리 중 오류가 발생했습니다."
                }
            }
        )

@router.get(
    "/me",
    response_model=MyProfileResponse
)
def get_my_profile(
    current_user: dict = Depends(get_current_user)
):
    return {
        "status": "success",
        "data": {
            "id": current_user["id"],
            "email": current_user["email"],
            "nickname": current_user["nickname"],
            "profile_image_url": current_user.get("profile_image_url"),
            "created_at": current_user["created_at"],
        }
    }