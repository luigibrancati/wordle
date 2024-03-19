from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..game_status import game_status


router = APIRouter(prefix='/debug')


@router.get("/solution", response_class=JSONResponse)
async def solution():
    return {"solution": game_status.solution}
