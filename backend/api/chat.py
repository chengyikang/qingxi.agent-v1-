"""聊天 API V1"""
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from services.chat import chat_service
from models.user import User
from api._helpers import ok, err

router = APIRouter(prefix="/api/chat", tags=["聊天"])

class ChatRequest(BaseModel):
    user_id: str = Field(..., description="用户ID")
    message: str = Field(..., min_length=1, max_length=5000, description="用户消息")

@router.post("")
async def send_message(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.id == request.user_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="用户不存在")
    result = await chat_service.process_message(user_id=request.user_id, message=request.message, db=db)
    if "error" in result:
        return err(result["error"])
    return ok(result)

@router.get("/history")
async def get_chat_history(user_id: str, limit: int = 50, db: AsyncSession = Depends(get_db)):
    histories = await chat_service.get_history_dict(user_id=user_id, db=db, limit=limit)
    return ok({"user_id": user_id, "histories": histories, "total": len(histories)})
