# Makefile for PhysAI-Brain-Bridge (Apple Silicon Optimized)

PLIST_NAME = com.physai.brainbridge.plist
PLIST_PATH = ~/Library/LaunchAgents/$(PLIST_NAME)

# PRISM_BRAIN을 위한 경로 설정
export PYTHONPATH := $(PYTHONPATH):$(PWD)/src/cognitive/prism_brain

# Apple Silicon(M1/M2/M3/M4) Homebrew 경로 설정
BREW_PREFIX = $(shell brew --prefix 2>/dev/null || echo "/opt/homebrew")
export CFLAGS = -I$(BREW_PREFIX)/include
export LDFLAGS = -L$(BREW_PREFIX)/lib

.PHONY: setup rmscli test run-server run-prism clean install-service uninstall-service status-service

# 1. 가상환경 구축 및 라이브러리 설치 (경로 문제 해결 버전)
setup:
	@command -v brew >/dev/null 2>&1 || { echo "Homebrew가 필요합니다. 'brew install portaudio'를 먼저 실행해주세요."; exit 1; }
	@command -v uv >/dev/null 2>&1 || { echo "uv가 필요합니다. 'curl -LsSf https://astral.sh/uv/install.sh | sh'로 설치해주세요."; exit 1; }
	
	# 시스템 라이브러리 확인
	@ls $(BREW_PREFIX)/include/portaudio.h >/dev/null 2>&1 || { echo "Error: portaudio가 없습니다. 'brew install portaudio'를 실행하세요."; exit 1; }
	
	uv venv
	uv pip install -r requirements.txt
	@echo "Setup complete. Virtual environment ready with Apple Silicon paths."

# 2. 시스템 초기 설정 (Robot Management System Initializer)
rmscli:
	uv run python3 scripts/setup_rms.py

# 3. 테스트 실행
test-audio:
	uv run pytest tests/audio/

test-network:
	uv run pytest tests/network/

# 4. 서버 및 지능 엔진 실행
run-server:
	uv run uvicorn src.server.main:app --host 0.0.0.0 --port 8000 --reload

run-prism:
	uv run python3 src/cognitive/prism_brain/run_brain.py

# 5. 서비스 등록 및 관리
install-service:
	cp $(PLIST_NAME) $(PLIST_PATH)
	launchctl load $(PLIST_PATH)
	@echo "Service installed and loaded successfully."

uninstall-service:
	launchctl unload $(PLIST_PATH) || true
	rm -f $(PLIST_PATH)
	@echo "Service uninstalled."

status-service:
	launchctl list | grep com.physai.brainbridge

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
