import math
from typing import Dict, Any, Tuple
from loguru import logger

class ConfidenceEngine:
    """
    LLM의 추론 확신도와 벡터 엔진의 유사도를 결합한 
    '인지적 신뢰도(Cognitive Confidence)' 엔진.
    """
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold

    def evaluate(self, 
                 llm_confidence: float, 
                 vector_distance: float, 
                 user_text: str) -> Tuple[float, bool, str]:
        """
        수학적으로 정교하게 신뢰도를 결합합니다.
        
        - llm_confidence: LLM이 스스로 판단한 확신도 (0~1)
        - vector_distance: 벡터 검색 최저 거리 (작을수록 정확)
        """
        
        # 1. 벡터 신뢰도 변환 (Sigmoid 함수 사용)
        # 거리가 0에 가까울수록 1.0에 수렴, 멀어질수록 0에 수렴
        vector_confidence = 1.0 / (1.0 + math.exp(5 * (vector_distance - 0.5)))

        # 2. 결합 신뢰도 계산 (베이지안 업데이트 개념 차용)
        # LLM의 고차원 추론과 벡터의 저차원 매칭 데이터를 결합
        # (LLM 가중치 0.7, 벡터 가중치 0.3)
        final_score = (llm_confidence * 0.7) + (vector_confidence * 0.3)

        # 3. 텍스트 패턴에 의한 예외 처리 (수학적 보정)
        # 문장 길이가 너무 길거나 복잡하면 보수적으로 점수 삭감
        length_penalty = 1.0
        if len(user_text.split()) > 5:
            length_penalty = 0.9 # 명령이 장황하면 신뢰도를 10% 깎음

        final_score *= length_penalty
        
        is_ambiguous = final_score < self.threshold
        
        reason = f"LLM Conf: {llm_confidence:.2f}, Vec Conf: {vector_confidence:.2f}, Final: {final_score:.2f}"
        
        return round(final_score, 4), is_ambiguous, reason
