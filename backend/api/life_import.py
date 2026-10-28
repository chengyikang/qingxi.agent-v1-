"""Life Import API - Module 01"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from models.life_import import LifeImport
from models.memory import Memory
from models.life_event import LifeEvent
from models.timeline import Timeline
from models.persona import Persona
from engines.life_import.engine import life_import_engine
from engines.life_parser.engine import life_parser_engine
from engines.persona.engine import persona_engine
from engines.life_memory.engine import life_memory_engine
from api._helpers import ok, err
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/life-import", tags=["Life Import"])

class ImportTextRequest(BaseModel):
    user_id: str = Field(..., description="用户ID")
    content: str = Field(..., description="文本内容")
    source_type: str = Field(default="auto", description="来源类型: auto/txt/markdown/qq_chat/wechat_chat/diary/note")
    file_name: str = Field(default="", description="文件名")

@router.post("/text")
async def import_from_text(request: ImportTextRequest, db = Depends(get_db)):
    """从文本内容导入人生资料"""
    try:
        # 创建导入记录
        import_record = LifeImport(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            source_type=request.source_type,
            file_name=request.file_name,
            status="processing",
            raw_content_preview=request.content[:1000],
        )
        db.add(import_record)
        await db.flush()
        
        # 执行导入
        result = await life_import_engine.import_from_text(
            user_id=request.user_id,
            content=request.content,
            source_type=request.source_type,
            file_name=request.file_name,
            db=db,
        )
        
        parsed_data = result.get("parsed_data", {})
        
        # 创建记忆
        memory_ids = []
        # 从 interests 创建记忆
        for interest in parsed_data.get("interests", []):
            mid = await life_memory_engine.create_memory(
                user_id=request.user_id,
                content=interest.get("name", ""),
                category="interest",
                layer="preference",
                importance=7,
                source="import",
                db=db,
            )
            if mid: memory_ids.append(mid)
        
        # 从 dreams 创建记忆
        for dream in parsed_data.get("dreams", []):
            mid = await life_memory_engine.create_memory(
                user_id=request.user_id,
                content=dream.get("dream", ""),
                category="dream",
                layer="preference",
                importance=8,
                source="import",
                db=db,
            )
            if mid: memory_ids.append(mid)
        
        # 从 values 创建记忆
        for value in parsed_data.get("values", []):
            mid = await life_memory_engine.create_memory(
                user_id=request.user_id,
                content=value.get("value", ""),
                category="identity",
                layer="identity",
                importance=8,
                source="import",
                db=db,
            )
            if mid: memory_ids.append(mid)
        
        # 创建人生事件
        event_ids = []
        for event in parsed_data.get("life_events", []):
            evt = LifeEvent(
                id=str(uuid.uuid4()),
                user_id=request.user_id,
                title=event.get("title", ""),
                event_type=event.get("type", "milestone"),
                impact_level={"high": 8, "medium": 5, "low": 3}.get(event.get("impact", "medium"), 5),
                source="import",
                source_id=import_record.id,
                confidence=0.7,
            )
            db.add(evt)
            event_ids.append(evt.id)
        
        await db.flush()
        
        # 更新人格
        try:
            await persona_engine.update_from_import(request.user_id, parsed_data, db)
        except Exception:
            pass  # 人格更新失败不影响导入
        
        # 更新导入记录
        import_record.status = "completed"
        import_record.parsed_data = parsed_data
        import_record.extracted_memory_count = len(memory_ids)
        import_record.extracted_event_count = len(event_ids)
        import_record.created_memory_ids = memory_ids
        import_record.created_event_ids = event_ids
        import_record.completed_at = datetime.utcnow()
        
        return ok({
            "import_id": import_record.id,
            "source_type": result.get("source_type"),
            "parsed_data": parsed_data,
            "memories_created": len(memory_ids),
            "events_created": len(event_ids),
        })
    except Exception as e:
        return err(str(e))

@router.post("/file")
async def import_from_file(
    user_id: str,
    file: UploadFile = File(...),
    db = Depends(get_db),
):
    """从文件导入人生资料"""
    try:
        content = (await file.read()).decode("utf-8")
        return await import_from_text(
            ImportTextRequest(
                user_id=user_id,
                content=content,
                source_type="auto",
                file_name=file.filename or "",
            ),
            db=db,
        )
    except Exception as e:
        return err(str(e))

@router.get("/history")
async def get_import_history(user_id: str, limit: int = 20, db = Depends(get_db)):
    """获取导入历史"""
    stmt = select(LifeImport).where(
        LifeImport.user_id == user_id, LifeImport.is_active == True
    ).order_by(LifeImport.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    imports = result.scalars().all()
    return ok({
        "imports": [
            {
                "id": i.id, "source_type": i.source_type, "file_name": i.file_name,
                "status": i.status, "extracted_memory_count": i.extracted_memory_count,
                "extracted_event_count": i.extracted_event_count,
                "created_at": i.created_at.isoformat(),
            }
            for i in imports
        ]
    })
