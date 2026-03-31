import json
import os
from typing import Dict, Any
from src.adapter.rms_loader import RMSLoader
from src.engine.vector_manager import VectorManager

class DataOrchestrator:
    def __init__(self, db_url: str, vector_db_path: str):
        self.rms_loader = RMSLoader(db_url)
        self.vector_manager = VectorManager(vector_db_path)

    def _prepare_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v if v is not None else "" for k, v in data.items()}

    def is_map_synced(self, map_id: int) -> bool:
        """해당 맵의 키워드 맵 파일이 존재하는지 확인합니다."""
        kw_map_filename = f"keyword_map_missions_map_{map_id}.json"
        kw_map_path = os.path.join("data", kw_map_filename)
        return os.path.exists(kw_map_path)

    def get_sync_count(self, map_id: int = None) -> int:
        """동기화할 미션 데이터 개수를 반환합니다."""
        missions = self.rms_loader.fetch_all_missions(map_id)
        return len(missions)

    def get_action_context(self) -> str:
        actions = self.rms_loader.fetch_all_actions()
        context_lines = [f"- ID: {act['action_id']}, 이름: {act['action_name']}, 코드: {act['command_code']}, 설명: {act['description']}" for act in actions if act['is_active'] == 1]
        return "\n".join(context_lines)

    def sync_global_actions(self):
        """기기나 맵에 상관없는 글로벌 액션들을 동기화합니다. 엔진 기동 시 1회 실행 권장."""
        print("[DataOrchestrator] 글로벌 액션 데이터 동기화 시작...")
        actions = self.rms_loader.fetch_all_actions()
        docs, metas, ids, keyword_map = [], [], [], {}

        if not actions:
            print("[DataOrchestrator] 경고: 조회된 액션 데이터가 없습니다. DB 연결을 확인하세요.")

        for act in actions:
            if act.get('is_active') == 0: continue
            prepared_act = self._prepare_metadata(act)
            name = prepared_act['action_name']
            docs.append(f"액션/명령어: {name}, 설명: {prepared_act['description']}, 타입: {prepared_act['action_type']}")
            metas.append({**prepared_act, "type": "action", "search_target": name})
            ids.append(f"action_{prepared_act['action_id']}")
            
            def reg(kw, a_id):
                if kw: keyword_map[kw] = keyword_map[kw.replace(" ", "")] = {"type": "action", "id": a_id, "name": name}
            
            reg(name, prepared_act['action_id'])
            aliases_raw = prepared_act.get('aliases')
            if aliases_raw:
                try:
                    aliases = json.loads(aliases_raw) if isinstance(aliases_raw, str) else aliases_raw
                    for alias in aliases: reg(alias, prepared_act['action_id'])
                except: pass

        # 글로벌 액션 키워드 맵 저장
        os.makedirs("data", exist_ok=True)
        with open("data/keyword_map_actions.json", "w", encoding="utf-8") as f:
            json.dump(keyword_map, f, ensure_ascii=False, indent=2)

        self.vector_manager.update_collection(collection_name="prism_actions", documents=docs, metadatas=metas, ids=ids)
        return {"status": "success", "count": len(ids), "message": "글로벌 액션 동기화 완료"}

    def sync_map_data(self, map_id: int):
        """특정 맵에 종속된 미션 데이터를 동기화합니다."""
        print(f"[DataOrchestrator] 맵(ID: {map_id}) 미션 데이터 동기화 시작...")
        missions = self.rms_loader.fetch_all_missions(map_id)
        docs, metas, ids, keyword_map = [], [], [], {}

        if not missions:
            print(f"[DataOrchestrator] 경고: 맵 ID {map_id}번에 조회된 미션 데이터가 없습니다.")

        for mis in missions:
            prepared_mis = self._prepare_metadata(mis)
            name = prepared_mis['mission_name']
            docs.append(f"미션/시나리오: {name}, 설명: {prepared_mis['description']}")
            metas.append({**prepared_mis, "type": "mission", "search_target": name})
            ids.append(f"mission_{prepared_mis['mission_id']}")
            
            m_info = {"type": "mission", "id": prepared_mis['mission_id'], "name": name}
            keyword_map[name] = keyword_map[name.replace(" ", "")] = m_info
            if "미션" not in name:
                keyword_map[f"{name} 미션"] = keyword_map[f"{name.replace(' ', '')}미션"] = m_info

        collection_name = f"prism_missions_map_{map_id}"
        kw_map_filename = f"keyword_map_missions_map_{map_id}.json"
        kw_map_path = os.path.join("data", kw_map_filename)
        
        with open(kw_map_path, "w", encoding="utf-8") as f:
            json.dump(keyword_map, f, ensure_ascii=False, indent=2)

        self.vector_manager.update_collection(collection_name=collection_name, documents=docs, metadatas=metas, ids=ids)
        return {"status": "success", "map_id": map_id, "count": len(ids), "message": f"맵 ID {map_id}번에 대한 미션 동기화 완료"}
