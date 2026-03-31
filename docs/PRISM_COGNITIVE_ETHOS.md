# PRISM: A Cognitive Architecture for Intuitive Human-Robot Interaction

## 1. 개요 (Abstract)
본 문서는 피지컬 AI(Physical AI)와 인간 사이의 의사소통 병목을 해결하기 위한 인지 엔진, **PRISM(Probabilistic Robotic Intent & Synthesis Module)**의 설계 철학과 기술적 구현을 다룬다. PRISM은 단순한 자연어 처리를 넘어, 로봇이 자신의 판단에 대한 **'인지적 확신(Cognitive Confidence)'**을 수학적으로 산출하고, 모호한 상황에서 인간과 상호작용(Tiki-taka)을 시도하는 '직관적 지능' 구현을 목표로 한다.

## 2. 설계 철학: 인간의 직관을 어떻게 수식화할 것인가?
인간의 직관은 단일 알고리즘이 아니라, **경험적 데이터(Memory)**와 **상황적 추론(Reasoning)**의 결합이다. PRISM은 이를 다음 세 가지 핵심 레이어로 구현한다.

### 2.1. 계층적 추론 (Tiered Inference Pipeline)
효율성과 정밀도를 동시에 잡기 위해 5단계 필터링 구조를 채택한다.
- **Tier 1~3 (Deterministic):** 완전 일치, 정규화, 정규 표현식을 통한 초고속 매칭.
- **Tier 4 (Semantic):** 벡터 데이터베이스(ChromaDB)를 통한 의미론적 유사도 검색.
- **Tier 5 (Agentic):** LLM(MLX 가속)을 통한 고차원 문맥 분석 및 자기 수정(Self-Correction) 파악.

### 2.2. 인지적 신뢰도 엔진 (Cognitive Confidence Engine)
사용자의 명령이 "앉았다가... 아니 그냥 앉아"와 같이 번복되거나 모호할 때, PRISM은 스스로의 확신도를 채점한다.
- **Sigmoid-based Vector Fusion:** 벡터 거리($d$)를 시그모이드 함수를 통해 신뢰도($C_v$)로 변환하여, 임계값 부근에서 인간의 '의구심'과 유사하게 급격히 감쇠하도록 설계한다.
  $$C_v = \frac{1}{1 + e^{k(d - \tau)}}$$
- **LLM Self-Reflection:** LLM이 자신의 추론 결과에 대해 스스로 부여한 확신 점수를 결합하여 최종 신뢰도($C_{final}$)를 도출한다.

### 2.3. 신체적 가중치 스코어러 (Embodied Weighted Scorer)
지능은 신체(Hardware)의 상태와 분리될 수 없다. 로봇의 배터리, 모터 온도, 현재 모드에 따라 특정 액션의 실행 가중치를 실시간으로 보정한다. 이는 TARS의 '정직도'나 '유머 감각' 설정처럼 로봇의 **'행동 편향성(Behavioral Bias)'**을 결정한다.

## 3. 구현의 정교함: 불확실성의 처리
PRISM이 "앉으라는 거야, 어쩌라는 거야?"라고 되묻는 과정은 단순한 에러 핸들링이 아니라, **확률적 로보틱스(Probabilistic Robotics)**의 실현이다. 
- **Ambiguity Detection:** 최종 신뢰도가 임계값($\tau = 0.8$) 미만일 경우 실행을 중단(Fail-safe).
- **Interactive Querying:** 불확실성의 원인을 분석(예: 논리적 충돌, 주저하는 어구)하여 인간에게 구체적인 질문을 던짐으로써 문맥을 재확인한다.

## 4. 결론 및 향후 과제
PRISM은 기계적인 명령 하달 구조를 '인간 대 인간'의 유연한 대화 구조로 변환한다. 향후 연구에서는 사용자의 음성 톤(Prosody)을 통한 감정 가중치 반영 및 멀티모달 비전 데이터를 결합한 '공간 인식적 직관'으로 확장될 예정이다.

---
**Keywords:** Physical AI, Cognitive Architecture, Human-Robot Interaction (HRI), Epistemic Uncertainty, LLM Reasoning, Embodied Intelligence.
