"""
QingXi V1 主入口
FastAPI 应用入口文件 - V1 完整版
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database.connection import init_db, close_db
from api import (
    user_router, chat_router, trust_router, memory_router,
    emotion_router, dashboard_router, analytics_router,
    persona_router, life_import_router, timeline_router,
    relationship_router, insight_router, reflection_router,
    life_profile_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print(f"启动 {settings.APP_NAME} V1...")
    await init_db()
    print("数据库初始化完成")
    print("V1 模块: CompanionEngine, PersonaEngine, LifeMemoryEngine, RelationshipEngine, InsightEngine, ReflectionEngine, LifeImportEngine, LifeParserEngine")
    yield
    print("关闭应用...")
    await close_db()
    print("数据库连接已关闭")


app = FastAPI(
    title=f"{settings.APP_NAME} V1",
    description="QingXi V1 - 理解用户人生的陪伴 Agent",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# V0 兼容路由
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(trust_router)
app.include_router(memory_router)
app.include_router(emotion_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)

# V1 新增路由
app.include_router(persona_router)
app.include_router(life_import_router)
app.include_router(timeline_router)
app.include_router(relationship_router)
app.include_router(insight_router)
app.include_router(reflection_router)
app.include_router(life_profile_router)


@app.get("/")
async def root():
    return {
        "name": f"{settings.APP_NAME} V1",
        "version": "1.0.0",
        "status": "running",
        "modules": [
            "CompanionEngine", "PersonaEngine", "LifeMemoryEngine",
            "RelationshipEngine", "InsightEngine", "ReflectionEngine",
            "LifeImportEngine", "LifeParserEngine",
        ],
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/info")
async def get_api_info():
    return {
        "name": f"{settings.APP_NAME} V1",
        "version": "1.0.0",
        "endpoints": {
            "user": "/api/user",
            "chat": "/api/chat",
            "trust": "/api/trust",
            "memory": "/api/memory",
            "emotion": "/api/emotion",
            "dashboard": "/api/dashboard",
            "analytics": "/api/analytics",
            "persona": "/api/persona",
            "life_import": "/api/life-import",
            "timeline": "/api/timeline",
            "relationship": "/api/relationship",
            "insight": "/api/insight",
            "reflection": "/api/reflection",
            "life_profile": "/api/life-profile",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
