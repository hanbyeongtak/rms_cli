# PhysAI-Brain-Bridge (Project TARS)

현시점 피지컬 AI와 로보틱스의 결합에서 발생하는 **'지능의 병목'**을 해결하기 위한 온디바이스 인지 엔진 & 통신 브리지 프로젝트입니다. 

---

## 🏗️ System Architecture

이 프로젝트는 다음과 같은 4-Layer 구조를 지향하며, 현재 **Cognitive Layer(Mac Mini)**와 **Bridge Layer(Robot SBC)** 간의 통신 최적화에 집중하고 있습니다.

- **`src/cognitive/`**: 의도 분류 및 VLA(Vision-Language-Action) 지능 레이어.
- **`src/bridge/`**: 로봇 하드웨어와 서버 간의 고성능 통신 브리지.
- **`src/server/`**: FastAPI 기반의 통합 관제 및 오디오 스트리밍 백엔드.
- **`web/`**: 아이폰 Safari 최적화 모바일 제어 인터페이스.

---

## 🤖 AI Collaboration (Gemini CLI)

이 프로젝트는 Gemini CLI를 통해 관리됩니다. 모든 개발 과정은 다음 원칙을 따릅니다.
- **`GEMINI.md`**: AI가 준수해야 할 프로젝트 핵심 원칙(Latency, Safety 등) 정의.
- **`docs/sessions/`**: 개발 세션별 기록을 통해 컨텍스트를 유지.
- **`tests/`**: 하드웨어 연동 특성상 모든 기능은 성능 테스트 코드를 동반.

---

## 🛠️ Getting Started

1. **환경 설정**:
   ```bash
   make setup
   ```
2. **테스트 실행**:
   - 오디오 파이프라인 테스트: `make test-audio`
   - 네트워크 레이턴시 테스트: `make test-network`
3. **서버 구동**:
   ```bash
   make run-server
   ```

---

## 🚀 Phase 1: Infrastructure & Connectivity (Current)

- [ ] **Task 1.1 (Audio):** RPi 5 - Mac Mini 간 무손실 오디오 스트리밍 검증.
- [ ] **Task 1.2 (Connectivity):** 유선 LAN 직결 0-레이턴시 핑퐁 및 데이터 무손실 구현.

---
