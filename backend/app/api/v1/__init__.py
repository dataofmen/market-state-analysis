from fastapi import APIRouter
from app.api.v1.endpoints import auth, symbols, watchlist, trades, analysis, data_update, settings

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(symbols.router, prefix="/symbols", tags=["symbols"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(data_update.router, prefix="/data", tags=["data"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
