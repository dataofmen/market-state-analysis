from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_watchlist():
    """관심 종목 목록 조회"""
    return {"message": "Get watchlist endpoint (구현 예정)"}


@router.post("/")
async def add_to_watchlist():
    """관심 종목 추가"""
    return {"message": "Add to watchlist endpoint (구현 예정)"}


@router.delete("/{watchlist_id}")
async def remove_from_watchlist(watchlist_id: int):
    """관심 종목 제거"""
    return {"message": f"Remove watchlist {watchlist_id} endpoint (구현 예정)"}
