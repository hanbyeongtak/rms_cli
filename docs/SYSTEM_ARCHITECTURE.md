# PhysAI-Brain-Bridge: System Architecture (TARS Paradigm)

본 문서는 **Project TARS**의 하드웨어 제어, 인지 추론, 그리고 배포 시스템에 대한 통합 아키텍처를 정의합니다.

## 1. 아키텍처 개요 (High-Level View)
전체 시스템은 **"Hybrid Edge-Cloud"** 구조를 따르며, 실시간 반응성은 로컬(Edge)에서, 관리 및 배포는 클라우드에서 담당합니다.

```text
[ USER ] <--- Audio/Web ---> [ Mac Mini (Edge Brain) ] <--- Local Net ---> [ Robot (Body) ]
                                     |
                                     +--- [ GitHub (Source) ]
                                     |
                                     +--- [ AWS RMS (Cloud Uplink) ]
```

## 2. 3대 핵심 레이어 (The Three Pillars)

### Layer A: Provisioning & Lifecycle (`rms-cli`)
- **진입점:** Homebrew를 통해 설치된 전용 CLI (`brew install rms-cli`).
- **인증(Auth):** 보안 인증키를 통한 시스템 권한 획득.
- **프로비저닝:** GitHub에서 `PRISM-Brain`, `Bridge` 등 핵심 모듈을 버전별로 동적 다운로드.
- **환경 구축:** `uv` 기반의 격리된 가상환경 자동 생성 및 의존성 해결.

### Layer B: Cognitive Intelligence (`PRISM-Brain`)
- **추론 엔진:** Apple Silicon(MLX) 최적화 로컬 LLM.
- **의도 분석:** 5단계 계층적 추론 (Exact -> Regex -> Vector -> LLM).
- **인지적 확신:** 수학적 모델(Sigmoid) 기반의 `Confidence Engine`으로 모호한 명령 시 되묻기(Tiki-taka) 수행.
- **세션 관리:** 로봇의 신체 상태와 대화 맥락을 결합한 멀티턴 메모리 유지.

### Layer C: Neuro-Bridge (`GateWay Server`)
- **통신 중계:** 로컬 네트워크(UDP/TCP)를 통한 로봇 SDK 하이레벨 제어.
- **텔레메트리:** 로봇의 배터리, 모터, 센서 데이터를 10Hz~ 이상의 주기로 수집.
- **안전 프로토콜:** 통신 두절 시 자동 비상 정지(Emergency Stop) 및 제약 조건 감시.

## 3. 데이터 흐름 (Data & Command Flow)

1. **Deployment Phase:** `rmscli` 실행 -> 인증 -> 깃 소스 동기화 -> 로봇 IP 탐색 -> 배포 확정.
2. **Operation Phase (Inference):**
   - 사용자 음성 -> Mac Mini (ASR) -> `PRISM-Brain` (의도 파악).
   - 의도(Intent) -> `Bridge Server` (명령 변환) -> 로봇 API 호출.
3. **Monitoring Phase:** 로봇 상태 -> `Bridge` -> AWS RMS (실시간 대시보드 및 로그 아카이빙).

## 4. 기술 스택 (Tech Stack)
- **Language:** Python 3.10+ (Core), TypeScript (Web UI).
- **Inference:** MLX (Apple Silicon Acceleration), ChromaDB (Vector DB).
- **Server:** FastAPI (Asynchronous Gateway), WebSockets (Real-time).
- **DevOps:** Homebrew (Distribution), Git Tags (Versioning), `uv` (Fast Package Management).

---
**Senior Architect's Note:** 
"지능은 격리된 뇌가 아니라, 환경과 소통하는 신체(Embodied)에서 완성됩니다. 본 아키텍처는 그 연결 고리를 가장 견고하고 빠르게 만드는 데 최적화되어 있습니다."
