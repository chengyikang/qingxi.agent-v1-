"""记忆 API V1"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from services.memory import memory_service
from engines.life_memory.engine import life_memory_engine
from models.user import User
from api._helpers import ok, err

router = APIRouter(prefix="/api/memory", tags=["记忆"])

@router.get("")
async def get_memories(
    user_id: str, limit: int = 50, layer: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    if layer:
        memories = await life_memory_engine.retrieve_by_layer(user_id, layer, limit, db)
    else:
        memories = await memory_service.get_user_memories(user_id, db, limit)
    return ok({"memories": memories, "total": len(memories)})

@router.get("/statistics")
async def get_memory_statistics(user_id: str, db: AsyncSession = Depends(get_db)):
    stats = await life_memory_engine.get_memory_statistics(user_id, db)
    return ok(stats)

@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, user_id: str, db: AsyncSession = Depends(get_db)):
    success = await memory_service.delete_memory(user_id, memory_id, db)
    return ok({"deleted": success})
