from typing import Dict, Any, List
from loguru import logger

class WeightedScorer:
    """
    로봇의 액션에 대해 상황별 가중치를 계산하는 엔진.
    PRISM_BRAIN의 의사결정을 고도화하는 핵심 모듈.
    """
    def __init__(self):
        self.system_mode = "normal" # normal, alert, battery_save, social

    def calculate_scores(self, capabilities: List[Dict[str, Any]], robot_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        기본 가중치와 실시간 상태를 결합하여 최종 점수(Final Score) 산출
        """
        scored_actions = []
        battery = robot_state.get("battery", 100)
        
        for cap in capabilities:
            base_weight = cap.get("base_weight", 0.5)
            energy_cost = cap.get("energy_cost", 0.1)
            final_score = base_weight

            # 1. 배터리에 따른 가중치 보정
            if battery < 20 and energy_cost > 0.5:
                final_score *= 0.1 # 배터리 없으면 무거운 동작 차단
                logger.warning(f"Low battery! De-weighting high energy action: {cap['name']}")

            # 2. 시스템 모드에 따른 보정
            if self.system_mode == "alert" and "alert" in cap.get("tags", []):
                final_score *= 2.0 # 감시 모드일 때 경고 동작 강조
            
            cap["final_score"] = round(final_score, 2)
            scored_actions.append(cap)
            
        return sorted(scored_actions, key=lambda x: x['final_score'], reverse=True)

    def get_prompt_context(self, scored_actions: List[Dict[str, Any]]) -> str:
        """LLM에게 전달할 고도화된 컨텍스트 문자열 생성"""
        context = "현재 로봇 액션 우선순위:\n"
        for act in scored_actions:
            status = "추천" if act['final_score'] > 0.7 else "일반"
            if act['final_score'] < 0.2: status = "제한됨"
            
            context += f"- {act['name']} (ID: {act['id']}): 점수 {act['final_score']} [{status}] - {act['description']}\n"
        return context
