# RMS (Robot Management System) Architecture Specification

## 1. Executive Summary
본 문서는 피지컬 AI(Physical AI)와 클라우드 로보틱스를 결합한 **Hybrid Edge-Cloud Orchestration** 아키텍처를 정의한다. 시스템은 초저지연 로컬 추론 엔진인 `PRISM-Brain`과 광역 관제 및 텔레메트리 분석을 담당하는 `AWS RMS Cloud`로 이원화되어 운영된다.

## 2. System Architecture Hierarchy

### 2.1. Layer 1: Physical Entity (The Body)
- **Devices:** Unitree Go2, Hiwonder PuppyPi 등.
- **Role:** 로우레벨 모터 제어 및 센서 데이터 수집.
- **Protocol:** 로컬 네트워크(UDP/TCP)를 통한 고속 통신.

### 2.2. Layer 2: Edge Brain (Mac Mini M4 Pro)
- **Role:** `GateWay Server` & `PRISM-Brain`.
- **Inference Engine:** Apple Silicon(MLX) 가속을 통한 온디바이스 의도 분류 및 행동 계획.
- **Session Management:** 멀티턴 대화 및 로봇 상태 동기화 관리.
- **Latency Target:** < 100ms (End-to-End).

### 2.3. Layer 3: Cloud Orchestrator (AWS RMS)
- **Role:** 글로벌 관제 서버 (Global Monitoring).
- **Telemetry:** 모든 로봇의 상태 및 로그를 DynamoDB/S3에 아카이빙.
- **Model Distribution:** 신규 학습된 ML 모델 및 설정값을 Edge Brain에 OTA(Over-The-Air) 배포.
- **Protocol:** MQTT / WebSockets (Secure Link).

## 3. Data Flow & Logic Path

### 3.1. Command Flow (Interaction Loop)
1. **Perception:** 로봇/마이크에서 음성 수집 -> Mac Mini 전송.
2. **Reasoning:** `PRISM-Brain`이 의도 파악 및 신뢰도(Confidence) 산출.
3. **Execution:** `Bridge Server`가 로봇 API 호출 (Low-latency path).
4. **Reporting:** 결과 및 텔레메트리를 AWS RMS로 전송 (Async path).

### 3.2. Hybrid Execution Strategy
- **Local Mode:** 인터넷 연결이 불안정한 환경에서도 핵심 기능(안전, 기본 이동) 유지.
- **Cloud Mode:** 복합적인 상황 분석이나 대규모 데이터 기반 의사결정 시 AWS의 고성능 인스턴스 활용.

## 4. Lifecycle & Deployment Strategy

### 4.1. Entry Point: Homebrew (`rms-cli`)
- **Distribution:** 사용자는 이미 구축된 `brew install rms-cli` 명령을 통해 시스템 관리 도구를 획득한다.
- **Execution:** Homebrew로 설치된 바이너리는 내부적으로 본 프로젝트의 `setup_rms.py` 코어 로직을 호출하여 프로비저닝을 시작한다.

### 4.2. Secure Provisioning Flow
1. **Handshake:** `rms-cli` 구동 시 사용자 인증(Auth Key)을 수행한다.
2. **Registry Sync:** 인증 성공 시, 허용된 버전 목록(Stable/Beta/Latest)을 원격 레지스트리(Git Tags)에서 가져온다.
3. **Component Pull:** 선택한 버전에 따라 `RMS-Link`, `PRISM-Brain`, `Robot-Drivers` 등의 핵심 모듈을 `git clone` 또는 `tarball` 형태로 로컬 맥미니에 배포한다.
4. **Environment Build:** `uv`를 활용하여 각 모듈에 최적화된 격리 가상환경을 자동 구축한다.

## 5. Safety & Constraints
- **Watchdog Timer:** Edge Brain과 로봇 간 통신 두절 시 자동 'Emergency Stop' 모드 진입.
- **Safety Override:** 로컬 하드웨어 제어권은 언제나 최우선 순위를 가짐 (Safety-First).

---
**Keywords:** Hybrid Cloud, Edge Computing, Physical AI, Telemetry, OTA Deployment.
