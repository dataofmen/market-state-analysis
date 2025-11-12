from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_settings():
    return {"message": "Get settings endpoint (구현 예정)"}


@router.put("/")
async def update_settings():
    return {"message": "Update settings endpoint (구현 예정)"}
