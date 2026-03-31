Project TARS: Comprehensive System Specification
0. Project Vision (The "North Star")
인터스텔라의 TARS처럼, 인간의 자연어 명령을 실시간 환경 데이터(Vision, LiDAR, Audio)와 결합하여 최적의 로봇 동작을 생성하고 실행하는 'Embodied Intelligence Platform' 구축.

1. System Architecture Hierarchy
이 프로젝트는 아래의 4가지 레이어가 유기적으로 연결된 거대 시스템입니다.

Layer A: Multimodal Perception (감각)
Audio: RODE 마이크를 통한 실시간 음성 수집 및 Ego-noise 필터링.

Vision/Spatial: LiDAR 및 카메라 데이터를 통한 환경 맵핑.

Proprioception: 로봇 관절 및 배터리 상태 모니터링.

Layer B: Cognitive Engine (뇌 - Mac Mini)
Speech-to-Intent: 단순 ASR을 넘어 문맥을 파악하는 의도 분류 모델.

VLA Planner: Vision-Language-Action 아키텍처를 통한 Long-horizon 작업 계획.

Decision Making: "집 치워" → [쓰레기 인식 → 경로 생성 → 로봇 팔 조작] 분해.

Layer C: Communication & Control Bridge (신경계)
Hybrid Protocol: 실시간 제어는 UDP/Socket, 관제 및 상태 보고는 MQTT.

Deterministic Link: 맥미니와 로봇 간 유선 LAN 직결로 지연 시간 최소화.

Layer D: User Experience (인터페이스 - Mobile Web)
Universal Control: 아이폰/웹 환경에서 로봇의 '눈'을 공유하고 모드(AI/Manual)를 전환.

2. Phase 1: Infrastructure & Connectivity (현 단계 목표)
현재 우리가 집중하는 부분은 Layer A와 Layer C의 기반을 닦는 것입니다. 신경계가 뚫려야 뇌(Cognitive)를 올릴 수 있기 때문입니다.

Task 1.1: High-Fidelity Audio Pipeline (tests/audio/)
목적: 로봇의 '귀'를 맥미니 '뇌'에 직결.

구체적 구현: RPi 5에서 수집한 RODE 오디오를 맥미니로 스트리밍하여 AI 모델이 학습/추론하기에 충분한 품질인지 검증.

Task 1.2: Central Command Hub (web/ & src/server/)
목적: 아이폰 웹앱 - 맥미니 - 로봇을 잇는 통합 관제 플랫폼 구축.

구체적 구현: FastAPI 기반 웹소켓 서버를 구축하여 아이폰에서 로봇 모드 전환 및 음성 명령 전달 테스트.

3. Gemini CLI용 모듈별 코딩 지침
[Module: Network Bridge]
src/bridge/에 로봇과 서버 간의 통신 클래스를 작성하라.

핵심: RobotAgent(RPi)와 BrainServer(Mac) 간의 핑퐁 테스트 및 데이터 유실율 측정 기능을 포함할 것.

[Module: Intent & VAD]
src/cognitive/에 음성 데이터 유무를 판단하는 VAD 노드를 구성하라.

핵심: 로봇 모터 구동 시 발생하는 고주파 노이즈를 Ignore할 수 있는 임계값 설정 기능을 포함할 것.

[Module: Mobile Interface]
web/에 아이폰 사파리 최적화 레이아웃을 작성하라.

핵심: Mode: Autonomous 버튼 클릭 시 맥미니의 AI 추론 루프가 활성화되고, Mode: Manual 시 조이스틱 UI가 나타나도록 설계하라.

4. 로드맵 및 한계 (Roadmap & Constraints)
초기 검증: 오디오/네트워크 유선 직결 테스트 (현재 위치).

지능 통합: 맥미니에 의도 분류 모델 및 VLA 시범 탑재.

다중 센서 융합: LiDAR 맵과 비전을 결합한 자율 이동 테스트.

최종 목표: 사용자의 추상적 명령("청소해")에 로봇이 10초 이상 복합 동작 수행.