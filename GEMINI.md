# GEMINI.md - PhysAI Brain-Bridge (Project TARS)

## 📌 Project Ethos
우리는 인터스텔라의 TARS와 같은 **'Embodied Intelligence'**를 지향한다. 모든 코드는 단순히 동작하는 것을 넘어, 로봇의 물리적 한계와 실시간성(Real-time)을 최우선으로 고려해야 한다.

## 🛠️ Mandatory Constraints (AI가 반드시 지켜야 할 원칙)
1. **Low Latency First:** 모든 네트워크 통신 및 추론 루프는 0.1초 이내의 레이턴시를 목표로 최적화한다.
2. **Hardware Resilience:** 로봇 하드웨어는 언제든 오프라인이 될 수 있다. 모든 Bridge 코드에는 'Timeout'과 'Re-connection' 로직이 필수다.
3. **Safety First:** 로봇 팔이나 모터 제어 명령 전송 전에는 반드시 'Emergency Stop' 및 'Validation' 로직을 거쳐야 한다.
4. **Context Preservation:** `docs/sessions/` 아래의 세션 로그를 참고하여, 이전 단계의 하드웨어 테스트 결과를 항상 반영한다.

## 📂 Directory Map
- `src/cognitive/`: 의도 분류, VLA, 센서 융합 등 지능형 레이어.
- `src/bridge/`: 로봇(SBC)과 서버(Mac Mini) 간의 통신/제어 브리지.
- `src/server/`: FastAPI 기반의 통합 관제 및 오디오 스트리밍 서버.
- `web/`: 아이폰 Safari 최적화 모바일 제어 인터페이스.
- `tests/`: 오디오 파이프라인(Task 1.1) 및 네트워크 핑퐁(Task 1.2) 테스트 코드.

## 📝 Ongoing Tasks (Task Tracker)
- [ ] **Infrastructure Setup:** 프로젝트 초기 구조 및 환경 설정 (진행 중)
- [ ] **Task 1.1 (Audio):** RPi 5 오디오 스트리밍 및 Mac Mini 수집 파이프라인 검증.
- [ ] **Task 1.2 (Connectivity):** 유선 LAN 기반 0-레이턴시 핑퐁 테스트 및 유실율 측정.
- [ ] **Task 2.1 (Cognitive):** 음성 의도 분류 기본 모델 이식.

## 💡 AI Interaction Rule
- 코드 생성 시 반드시 `loguru`를 사용하여 하드웨어 이벤트를 상세히 로깅할 것.
- 새로운 모듈 추가 시 `tests/`에 해당하는 검증 스크립트를 세트로 제안할 것.
