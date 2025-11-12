from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_trades():
    return {"message": "List trades endpoint (구현 예정)"}


@router.post("/")
async def create_trade():
    return {"message": "Create trade endpoint (구현 예정)"}


@router.put("/{trade_id}")
async def update_trade(trade_id: int):
    return {"message": f"Update trade {trade_id} endpoint (구현 예정)"}


@router.delete("/{trade_id}")
async def delete_trade(trade_id: int):
    return {"message": f"Delete trade {trade_id} endpoint (구현 예정)"}
