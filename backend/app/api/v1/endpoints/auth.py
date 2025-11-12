from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
async def register():
    """회원가입"""
    return {"message": "Register endpoint (구현 예정)"}


@router.post("/login")
async def login():
    """로그인"""
    return {"message": "Login endpoint (구현 예정)"}


@router.post("/refresh")
async def refresh_token():
    """토큰 갱신"""
    return {"message": "Refresh token endpoint (구현 예정)"}
