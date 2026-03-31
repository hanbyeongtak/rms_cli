import logging
import json
from sqlalchemy import create_engine, text
from typing import List, Dict, Any

class RMSLoader:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)

    def fetch_all_actions(self) -> List[Dict[str, Any]]:
        query = text("""
            SELECT 
                action_id, action_name, command_code, description, action_type, tts_msg, is_active, aliases
            FROM actions_info
            WHERE is_active = 1
        """)
        
        results = []
        try:
            with self.engine.connect() as conn:
                rows = conn.execute(query).mappings().fetchall()
                for row in rows:
                    results.append(dict(row))
        except Exception as e:
            print(f"[RMSLoader] 액션 조회 실패: {e}")
            
        return results

    def check_map_exists(self, map_id: int) -> bool:
        
        query = text("SELECT COUNT(*) as cnt FROM maps_info WHERE map_id = :map_id")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"map_id": map_id}).fetchone()
                return result[0] > 0
        except Exception as e:
            print(f"[RMSLoader] 맵 존재 여부 확인 실패 (maps_info): {e}")
            return False

    def fetch_all_missions(self, map_id: int = None) -> List[Dict[str, Any]]:
        query_text = """
            SELECT 
                mission_id, mission_name, description, map_id
            FROM missions_info
        """
        if map_id:
            query_text += " WHERE map_id = :map_id"
        
        query = text(query_text)
        
        results = []
        try:
            with self.engine.connect() as conn:
                params = {"map_id": map_id} if map_id else {}
                rows = conn.execute(query, params).mappings().fetchall()
                for row in rows:
                    results.append(dict(row))
        except Exception as e:
            print(f"[RMSLoader] 미션 조회 실패: {e}")
            
        return results

    def get_map_id_by_device(self, device_id: int) -> int | None:
        """디바이스 ID를 통해 매핑된 맵 ID를 조회"""
        query = text("SELECT map_id FROM devices_info WHERE device_id = :device_id")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"device_id": device_id}).mappings().fetchone()
                return result['map_id'] if result else None
        except Exception as e:
            print(f"[RMSLoader] 디바이스 맵 조회 실패: {e}")
            return None

    def get_lidar_id_by_map_id(self, map_id: int) -> int | None:
        """map ID를 통해 lidar id 조회 """
        query = text("SELECT lidar_folder_name FROM devices_info WHERE map_id = :map_id")
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"map_id": map_id}).mappings().fetchone()
                return result['lidar_folder_name'] if result else None
        except Exception as e:
            print(f"[RMSLoader] lidar_folder_name 조회 실패: {e}")
            return None