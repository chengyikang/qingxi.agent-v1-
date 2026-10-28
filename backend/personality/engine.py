"""人格引擎 V0 (兼容层，V1 由 PersonaEngine 替代)"""
from typing import Dict, List


class PersonalityEngine:
    def __init__(self):
        self.growth_factors = {
            "openness": {"base": 0.3, "trust_weight": 0.7},
            "initiative": {"base": 0.2, "trust_weight": 0.5},
            "vulnerability": {"base": 0.15, "trust_weight": 0.8},
        }
    
    def calculate_growth(self, trust_growth: int) -> Dict[str, float]:
        growth = {}
        for dimension, factors in self.growth_factors.items():
            g = (factors["base"] + factors["trust_weight"] * trust_growth / 100) * trust_growth / 10
            growth[dimension] = min(round(g, 2), 2.0)
        return growth
    
    def apply_growth(self, current: Dict[str, int], growth: Dict[str, float]) -> Dict[str, int]:
        new_state = {}
        for dimension in ["openness", "initiative", "vulnerability"]:
            new_val = current.get(dimension, 0) + int(growth.get(dimension, 0) * 10)
            new_state[dimension] = max(0, min(100, new_val))
        return new_state
    
    def get_personality_description(self, state: Dict[str, int]) -> str:
        parts = []
        o = state.get("openness", 10)
        i = state.get("initiative", 5)
        v = state.get("vulnerability", 0)
        if o < 20: parts.append("谨慎")
        elif o < 50: parts.append("适度坦诚")
        else: parts.append("坦诚")
        if i < 10: parts.append("被动")
        elif i < 20: parts.append("适度主动")
        else: parts.append("主动")
        if v < 20: parts.append("坚强")
        elif v < 50: parts.append("偶尔脆弱")
        else: parts.append("愿意展现脆弱")
        return "、".join(parts)
    
    def get_response_guidance(self, state: Dict[str, int]) -> Dict[str, str]:
        guidance = {}
        o = state.get("openness", 10)
        i = state.get("initiative", 5)
        v = state.get("vulnerability", 0)
        if o < 20: guidance["openness"] = "保持谨慎，回复简洁"
        elif o < 50: guidance["openness"] = "可以适度分享"
        else: guidance["openness"] = "可以坦诚表达"
        if i < 10: guidance["initiative"] = "被动回应为主"
        elif i < 20: guidance["initiative"] = "可以适当提问"
        else: guidance["initiative"] = "主动关心用户"
        if v < 20: guidance["vulnerability"] = "保持坚强"
        elif v < 50: guidance["vulnerability"] = "可以适度表露感受"
        else: guidance["vulnerability"] = "可以分享内心感受"
        return guidance


personality_engine = PersonalityEngine()
