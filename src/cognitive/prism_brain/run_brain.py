import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from loguru import logger
import os
import sys

# PRISM_BRAIN의 내부 모듈을 참조하기 위해 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# PRISM의 핵심 클래스들 (이식된 위치에서 import)
# PYTHONPATH 설정 덕분에 src 폴더 내부의 모듈들을 바로 참조할 수 있습니다.
from src.engine.intent_classifier import IntentClassifier
from src.core.data_orchestrator import DataOrchestrator

app = FastAPI(title="PRISM_BRAIN Intelligence Server")

# 인스턴스 초기화 (경로 설정 주의)
# 실제 데이터 경로와 DB URL은 설정 파일에서 읽어와야 함
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
VECTOR_DB_PATH = os.path.join(DATA_DIR, "chroma_db")

# TODO: 실제 연동 시 DB URL 등 환경 변수 처리 필요
orchestrator = DataOrchestrator(db_url="sqlite:///prism.db", vector_db_path=VECTOR_DB_PATH)
# 초기화 시 글로벌 액션 동기화 등 필요할 수 있음

class CommandRequest(BaseModel):
    text: str
    action_context: Optional[str] = ""
    map_id: Optional[int] = None

@app.on_event("startup")
async def startup_event():
    logger.info("PRISM_BRAIN Server starting up...")
    # 여기서 모델 로딩이나 벡터 스토어 준비 작업 수행

@app.get("/health")
async def health_check():
    return {"status": "ok", "engine": "PRISM_BRAIN"}

@app.post("/analyze")
async def analyze_command(request: CommandRequest):
    """
    사용자의 자연어 명령을 분석하여 의도(Intent)를 반환합니다.
    """
    logger.info(f"Analyzing command: {request.text}")
    
    # 1. Classifier 생성 (실제 운영 시에는 싱글톤으로 관리 추천)
    from engine.vector_manager import VectorManager
    vm = VectorManager(VECTOR_DB_PATH)
    classifier = IntentClassifier(vector_manager=vm)
    
    # 2. 맵 컨텍스트 로드
    classifier.load_map_context(request.map_id)
    
    # 3. 의도 분류 실행
    result = classifier.classify(request.text, request.action_context)
    
    if not result or result.get("method") == "fail":
        logger.warning(f"Failed to classify intent for: {request.text}")
        return {"status": "unknown", "intent": None}

    logger.success(f"Intent classified: {result.get('method')}")
    return {"status": "success", "intent": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
