from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_symbols():
    """종목 목록 조회"""
    return {"message": "List symbols endpoint (구현 예정)"}


@router.get("/{symbol}")
async def get_symbol(symbol: str):
    """종목 상세 조회"""
    return {"message": f"Get symbol {symbol} endpoint (구현 예정)"}


@router.get("/search")
async def search_symbols(query: str):
    """종목 검색"""
    return {"message": f"Search symbols: {query} (구현 예정)"}
