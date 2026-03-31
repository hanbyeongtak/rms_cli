import json
import logging
import re
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, List

class MissionBuilder:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        logging.basicConfig(level=logging.DEBUG) 

    def build_mission_json(self, mission_id) -> str | None:
        logging.debug(f"[MissionBuilder] Start building mission JSON for ID: {mission_id}")
        try:
            with self.engine.connect() as conn:
                mission_query = text("SELECT mission_id, mission_name, map_id FROM missions_info WHERE mission_id = :mid")
                mission_info = conn.execute(mission_query, {"mid": mission_id}).mappings().fetchone()

                if not mission_info:
                    logging.warning(f"[MissionBuilder] Mission ID {mission_id} not found.")
                    return None

                lidar_folder = ""
                try:
                    lidar_query = text("SELECT lidar_folder_name FROM devices_info WHERE map_id = :map_id LIMIT 1")
                    lidar_res = conn.execute(lidar_query, {"map_id": mission_info['map_id']}).mappings().fetchone()
                    if lidar_res:
                        lidar_folder = lidar_res['lidar_folder_name']
                except Exception as le:
                    logging.warning(f"[MissionBuilder] Failed to fetch lidar_folder: {le}")

                safe_name = re.sub(r'\s+', '_', mission_info['mission_name']) 
                mission_key = f"mission_{mission_info['mission_id']:02d}_{safe_name}"

                steps_query = text("""
                    SELECT item_id, step_order
                    FROM mission_items
                    WHERE mission_id = :mid
                    ORDER BY step_order ASC
                """)
                steps = conn.execute(steps_query, {"mid": mission_id}).mappings().fetchall()

                formatted_steps = []
                for step in steps:
                    step_id = step['item_id']
                    step_data = {
                        "step_order": step['step_order'],
                        "start_actions": {"payload": self._fetch_actions(conn, "start_actions", step_id)},
                        "mid_actions": {"payload": self._fetch_actions(conn, "mid_actions", step_id)},
                        "end_actions": {"payload": self._fetch_actions(conn, "end_actions", step_id)}
                    }
                    formatted_steps.append(step_data)

                result = {
                    mission_key: {
                        "lidar": lidar_folder,
                        "mission_id": f"mission_{mission_info['mission_id']:02d}", 
                        "mission_name": mission_info['mission_name'],
                        "steps": formatted_steps,
                    }
                }
                return json.dumps(result, ensure_ascii=False, indent=4)

        except Exception as e:
            logging.error(f"[MissionBuilder] Error building mission: {e}", exc_info=True)
            return None

    def build_sequence_recipe(self, action_results: List[Dict[str, Any]]) -> str | None:
        """자연어 명령을 통한 동적 시퀀스 생성 (페이즈 테이블을 사용하지 않음)"""
        logging.debug(f"[MissionBuilder] Building sequence recipe for {len(action_results)} actions")
        try:
            with self.engine.connect() as conn:
                formatted_steps = []
                for idx, res in enumerate(action_results):
                    aid = res['id']
                    custom_params = res.get('params', {})
                    
                    query = text("SELECT * FROM actions_info WHERE action_id = :aid")
                    act = conn.execute(query, {"aid": aid}).mappings().fetchone()
                    if not act: continue

                    final_params = {}
                    if act['is_params'] and act['action_params']:
                        try:
                            params_data = json.loads(act['action_params']) if isinstance(act['action_params'], str) else act['action_params']
                            final_params.update(params_data)
                        except: pass
                    
                    # 동적 생성 명령에서는 target_group이 DB에 없으므로 custom_params를 통해서만 전달됨
                    final_params.update(custom_params)

                    action_item = {
                        "command_code": act['command_code'],
                        "params": final_params,
                        "tts_content": act['tts_msg']
                    }

                    formatted_steps.append({
                        "step_order": idx + 1,
                        "start_actions": {"payload": []},
                        "mid_actions": {"payload": [action_item]},
                        "end_actions": {"payload": []}
                    })

                if not formatted_steps: return None

                if len(formatted_steps) == 1:
                    act_info = action_results[0]
                    mission_key = f"action_{act_info['id']}"
                    mission_id = f"single_action_{act_info['id']}"
                    mission_display_name = act_info.get('name', '단일 동작')
                else:
                    mission_key = f"dynamic_seq_{len(formatted_steps)}"
                    mission_id = "dynamic_sequence"
                    mission_display_name = "복합 명령 실행"

                result = {mission_key: {"mission_id": mission_id, "mission_name": mission_display_name, "steps": formatted_steps}}
                return json.dumps(result, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"[MissionBuilder] Sequence build error: {e}")
            return None

    def _fetch_actions(self, conn, table_name: str, item_id: int) -> List[Dict[str, Any]]:
        """미션의 각 페이즈 테이블(start/mid/end_actions)에서 액션 정보를 가져옴"""
        pos_join = ""
        pos_cols = ""
        if table_name in ["start_actions", "end_actions"]:
            pos_cols = """, 
                p.label, p.pos_x, p.pos_y, p.pos_z, 
                p.uv_x, p.uv_y, p.uv_z, p.rotation, p.tilt"""
            pos_join = f"LEFT JOIN positions_info p ON ph.position_id = p.position_id"

        # [핵심 수정] target_group을 a(actions_info)가 아닌 ph(phase 테이블)에서 가져옴
        query = text(f"""
            SELECT 
                a.command_code, a.action_params, a.is_params,
                ph.target_group, ph.tts_msg as phase_tts, a.tts_msg as default_tts
                {pos_cols}
            FROM {table_name} ph
            JOIN actions_info a ON ph.action_id = a.action_id
            {pos_join}
            WHERE ph.item_id = :iid AND ph.is_active = 1
            ORDER BY ph.seq_num ASC
        """)

        try:
            rows = conn.execute(query, {"iid": item_id}).mappings().fetchall()
            payload = []
            for row in rows:
                item = {"command_code": row['command_code']}
                final_params = {}
                
                # 1. 기본 파라미터 로드
                if 'pos_x' in row and row['pos_x'] is not None:
                    final_params = {
                        "id": row['label'], "x": row['pos_x'], "y": row['pos_y'], "z": row['pos_z'],
                        "uv_x": row['uv_x'], "uv_y": row['uv_y'], "uv_z": row['uv_z'],
                        "rotation": row['rotation'], "tilt": row['tilt']
                    }
                elif row['is_params'] and row['action_params']:
                    try:
                        final_params = json.loads(row['action_params']) if isinstance(row['action_params'], str) else row['action_params']
                    except: pass
                
                # 2. 페이즈 전용 target_group 주입
                if 'target_group' in row and row['target_group']:
                    final_params['target_group'] = row['target_group']
                    logging.debug(f"[MissionBuilder] Fetched target_group from {table_name}: {row['target_group']}")

                item['params'] = final_params
                tts = row['phase_tts'] if row['phase_tts'] else row['default_tts']
                if tts: item['tts_content'] = tts
                
                payload.append(item)
            return payload
        except Exception as e:
            logging.error(f"[MissionBuilder] _fetch_actions error: {e}")
            return []
