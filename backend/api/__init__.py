"""API 模块 V1"""
from api.user import router as user_router
from api.chat import router as chat_router
from api.trust import router as trust_router
from api.memory import router as memory_router
from api.emotion import router as emotion_router
from api.dashboard import router as dashboard_router
from api.analytics import router as analytics_router
from api.persona import router as persona_router
from api.life_import import router as life_import_router
from api.timeline import router as timeline_router
from api.relationship import router as relationship_router
from api.insight import router as insight_router
from api.reflection import router as reflection_router
from api.life_profile import router as life_profile_router

__all__ = [
    "user_router", "chat_router", "trust_router", "memory_router",
    "emotion_router", "dashboard_router", "analytics_router",
    "persona_router", "life_import_router", "timeline_router",
    "relationship_router", "insight_router", "reflection_router",
    "life_profile_router",
]
