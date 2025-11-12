from fastapi import APIRouter

router = APIRouter()


@router.get("/history")
async def get_analysis_history():
    return {"message": "Get analysis history endpoint (구현 예정)"}
