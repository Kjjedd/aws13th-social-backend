from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from core.limiter import limiter
from routers.users import router as users_router
from routers.session import router as session_router


app = FastAPI(
    title="Cloud Community API",
    version="1.0.0"
)
#SlowAPI 설정
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
#로깅 설정
logging.basicConfig(level=logging.INFO)
#라우터 등록
app.include_router(users_router)
app.include_router(session_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    _ = request
    error = exc.errors()[0]  # 첫 번째 에러만 사용
    field = error["loc"][-1]

    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": f"{field}은(는) 올바른 형식이 아닙니다.",
                "details": {
                    "field": field
                }
            }
        }
    )

#Rate Limit 초과 핸들러
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "요청이 너무 많습니다. 잠시 후 다시 시도해주세요."
            }
        }
    )
