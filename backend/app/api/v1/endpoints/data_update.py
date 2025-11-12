from fastapi import APIRouter

router = APIRouter()


@router.post("/update")
async def trigger_data_update():
    return {"message": "Trigger data update endpoint (구현 예정)"}
