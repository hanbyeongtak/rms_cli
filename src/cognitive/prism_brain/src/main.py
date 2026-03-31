from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml, os, sys, json, time, requests, asyncio

sys.path.append(os.getcwd())

from src.adapter.mission_builder import MissionBuilder
from src.core.data_orchestrator import DataOrchestrator
from src.engine.intent_classifier import IntentClassifier
from src.engine.vector_manager import VectorManager
from src.engine.mlx_engine import MLXEngine, ActionParserAgent

class HealthStatus(BaseModel):
    status: str
    current_map_id: int | None = None

class UserCommand(BaseModel):
    text: str

class CommandResponse(BaseModel):
    intent: str
    confidence: str
    target_id: int | str | None = None
    target_name: str | None = None
    payload: dict | None = None
    message: str
    method: str
    latency_ms: float
    trace_log: dict | None = None

class PrismBootLoader:
    @staticmethod
    def get_config():
        config_path = "config/prism_config.yaml"
        vector_db_path = "data/chroma_db"
        llm_model_id = None
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            db_url = config.get("system", {}).get("rms_db_url", "")
            vector_db_path = config.get("paths", {}).get("vector_db_path", vector_db_path)
            llm_model_id = config.get("models", {}).get("llm", {}).get("model_id")
        else:
            db_url = os.environ.get("RMS_DB_URL", "")
        return db_url, vector_db_path, llm_model_id

    @staticmethod
    def load_components(db_url: str, vector_db_path: str, llm_model_id: str = None):
        os.makedirs("data", exist_ok=True)
        try:
            mb, vm, do = MissionBuilder(db_url), VectorManager(vector_db_path), DataOrchestrator(db_url, vector_db_path)
            parser_agent = None
            if llm_model_id:
                try: parser_agent = ActionParserAgent(MLXEngine(llm_model_id))
                except Exception as e: print(f"[>>> EJ_ERROR] Agentic LLM 로드 실패: {e}")
            ic = IntentClassifier(vm, parser_agent=parser_agent)
            return mb, ic, do
        except Exception as e:
            print(f"[>>> EJ_ERROR] 컴포넌트 로딩 중 치명적 오류: {e}")
            raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_url, vector_db_path, llm_model_id = PrismBootLoader.get_config()
    mb, ic, do = PrismBootLoader.load_components(db_url, vector_db_path, llm_model_id)
    app.state.mission_builder, app.state.intent_classifier, app.state.data_orchestrator = mb, ic, do
    app.state.current_map_id = None
    async def delayed_sync():
        await asyncio.sleep(1.5) 
        try:
            loop = asyncio.get_event_loop()
            print("[>>> EJ_DEBUG] 백그라운드 글로벌 동기화 시작...")
            await loop.run_in_executor(None, do.sync_global_actions)
            await loop.run_in_executor(None, ic.load_map_context, None)
            print("[>>> EJ_DEBUG] 백그라운드 글로벌 동기화 및 컨텍스트 로드 완료.")
        except Exception as e: print(f"[>>> EJ_ERROR] 백그라운드 동기화 중 오류: {e}")
    asyncio.create_task(delayed_sync())
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health", response_model=HealthStatus)
async def health_check(request: Request): return {"status": "ok", "current_map_id": request.app.state.current_map_id}

@app.get("/keywords")
async def get_keywords(request: Request): return request.app.state.intent_classifier.keyword_map

@app.get("/system/sync/{map_id}")
async def sync_vector_db_by_map(map_id: int, request: Request, background_tasks: BackgroundTasks):
    orchestrator: DataOrchestrator = request.app.state.data_orchestrator
    classifier: IntentClassifier = request.app.state.intent_classifier
    if not orchestrator.rms_loader.check_map_exists(map_id):
        return {"status": "error", "map_id": map_id, "message": f"맵 ID {map_id}번에 대한 데이터를 찾을 수 없습니다."}
    total_count = orchestrator.get_sync_count(map_id)
    def run_sync_task(m_id):
        callback_url = os.environ.get("FRONTEND_CALLBACK_URL", "http://localhost:8100/api/robot/missions_info/sync/update")
        try:
            result = orchestrator.sync_map_data(m_id)
            classifier.load_map_context(m_id)
            request.app.state.current_map_id = m_id
            try: requests.post(callback_url, json={"map_id": m_id, "sync_state": 1}, timeout=5)
            except: pass
        except:
            try: requests.post(callback_url, json={"map_id": m_id, "sync_state": 0}, timeout=5)
            except: pass
    background_tasks.add_task(run_sync_task, map_id)
    return {"status": "accepted", "map_id": map_id, "total_count": total_count, "message": f"맵 ID {map_id}번에 대한 동기화를 시작합니다."}

@app.post("/system/active-map/{map_id}")
async def set_active_map(map_id: int, request: Request):
    orchestrator: DataOrchestrator = request.app.state.data_orchestrator
    classifier: IntentClassifier = request.app.state.intent_classifier
    if not orchestrator.rms_loader.check_map_exists(map_id): return {"status": "error", "message": f"유효하지 않은 맵 ID {map_id}번입니다."}
    if classifier.load_map_context(map_id):
        request.app.state.current_map_id = map_id
        return {"status": "success", "active_map_id": map_id}
    return {"status": "error", "message": "데이터 로드 실패"}

@app.post("/system/active-device/{device_id}")
async def set_active_device(device_id: int, request: Request):
    orchestrator: DataOrchestrator = request.app.state.data_orchestrator
    classifier: IntentClassifier = request.app.state.intent_classifier
    try:
        map_id = orchestrator.rms_loader.get_map_id_by_device(device_id)
        if map_id is None: return {"status": "error", "message": "맵 정보 없음"}
        if not orchestrator.rms_loader.check_map_exists(map_id): return {"status": "error", "message": "유효하지 않은 맵"}
        if not orchestrator.is_map_synced(map_id): orchestrator.sync_map_data(map_id)
        if classifier.load_map_context(map_id):
            request.app.state.current_map_id = map_id
            return {"status": "success", "device_id": device_id, "active_map_id": map_id}
        return {"status": "error", "message": "로드 실패"}
    except Exception as e: return {"status": "error", "message": str(e)}

@app.post("/command", response_model=CommandResponse)
async def process_command(cmd: UserCommand, request: Request):
    start_time = time.perf_counter()
    classifier, builder, orchestrator = request.app.state.intent_classifier, request.app.state.mission_builder, request.app.state.data_orchestrator
    text = cmd.text
    
    # [시각화 로그] 요청 시작
    print(f"\n{'='*60}")
    print(f"[REQUEST] Input: '{text}' (Map: {request.app.state.current_map_id})")
    print(f"{'-'*60}")
    
    classification = classifier.classify(text, action_context=orchestrator.get_action_context())
    method = classification['method']
    trace_log = {"classification_raw": {k: v for k, v in classification.items() if k not in ['results', 'result']}, "input_length": len(text), "map_id": request.app.state.current_map_id}

    def finalize_response(intent, confidence, target_id=None, target_name=None, payload=None, message=""):
        latency = (time.perf_counter() - start_time) * 1000
        # [시각화 로그] 결과 요약
        print(f"[RESULT] Intent: {intent}, Method: {method}, Latency: {latency:.2f}ms")
        if payload:
            print(f"[RECIPE] Generated JSON Payload:\n{json.dumps(payload, indent=4, ensure_ascii=False)}")
        else:
            print(f"[FAILED] Message: {message}")
        print(f"{'='*60}\n")
        
        return CommandResponse(intent=intent, confidence=confidence, target_id=target_id, target_name=target_name, payload=payload, message=message, method=method, latency_ms=round(latency, 2), trace_log=trace_log)

    if method == 'fail':
        return finalize_response("unknown", "low", message="죄송합니다. 이해할 수 없는 명령입니다.")

    results = classification.get('results', [])
    if len(results) > 1:
        recipe_json = builder.build_sequence_recipe(results)
        if recipe_json:
            return finalize_response(intent="sequence_action", confidence="high" if method != 'agentic_llm' else "medium", payload=json.loads(recipe_json), message=f"분석된 {len(results)}개의 동작을 순차적으로 실행합니다.")

    result = classification.get('result') or (results[0] if len(results) == 1 else None)
    if result:
        try: target_id = int(result['id'])
        except: target_id = result['id']
        target_type, target_name = result.get('type'), result.get('name', '')
        if not target_type or target_type == 'action':
            if clean_name := result.get('name'):
                if info := classifier.keyword_map.get(clean_name): target_type = info['type']
        target_type = target_type or 'action'
        
        recipe_json = builder.build_mission_json(target_id) if target_type == 'mission' else builder.build_sequence_recipe([result])
        intent_type = "mission_execution" if target_type == 'mission' else "single_action"
        if recipe_json:
            return finalize_response(intent=intent_type, confidence="high", target_id=target_id, target_name=target_name, payload=json.loads(recipe_json), message=f"'{target_name or target_id}'을(를) 실행합니다.")
            
    return finalize_response("unknown", "low", message="실행 레시피 생성 실패")

@app.post("/mission/generate/{mission_id}")
async def generate_mission_recipe(mission_id: int, request: Request):
    builder = request.app.state.mission_builder
    try:
        mission_json = builder.build_mission_json(mission_id)
        if mission_json:
            print(f"\n[DIRECT GENERATE] Mission ID: {mission_id}")
            print(f"[RECIPE] Generated JSON:\n{mission_json}\n")
            return json.loads(mission_json)
        return {"status": "error", "message": "미션 없음"}
    except Exception as e: return {"status": "error", "message": str(e)}
