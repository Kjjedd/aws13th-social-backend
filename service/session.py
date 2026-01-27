import logging
from typing import Dict, Any

from schemas.session import SessionCreate
from utils.data import load_json
from utils.auth import verify_password, create_access_token

logger = logging.getLogger(__name__)


class AuthenticationFailedError(Exception):
    pass


def authenticate_user(session: SessionCreate) -> Dict[str, Any]:
    """
    이메일/비밀번호 인증 후 JWT 발급
    """
    users = load_json("users.json")

    # 이메일로 사용자 조회
    user = next(
        (u for u in users if u["email"] == session.email),
        None
    )

    # 이메일이 없거나
    if user is None:
        logger.info("로그인 실패: 존재하지 않는 이메일")
        raise AuthenticationFailedError()

    # 비밀번호 검증
    if not verify_password(session.password, user["password"]):
        logger.info("로그인 실패: 비밀번호 불일치")
        raise AuthenticationFailedError()

    # JWT 발급
    access_token = create_access_token(user["id"])

    return {
        "status": "success",
        "data": {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
        }
    }