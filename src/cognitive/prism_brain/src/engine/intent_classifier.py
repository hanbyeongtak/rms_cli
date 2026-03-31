import json
import re
import os
import logging
from typing import Dict, Any, List
from src.engine.vector_manager import VectorManager
from src.engine.mlx_engine import ActionParserAgent

class IntentClassifier:
    def __init__(self, vector_manager: VectorManager, parser_agent: ActionParserAgent = None):
        self.vector_manager = vector_manager
        self.parser_agent = parser_agent
        self.keyword_map = {}
        self.current_map_id = None
        
        self.korean_nums = {
            "한": 1, "두": 2, "세": 3, "네": 4, "다섯": 5, "여섯": 6, "일곱": 7, "여덟": 8, "아홉": 9, "열": 10,
            "일": 1, "이": 2, "삼": 3, "사": 4, "오": 5, "육 :": 6, "칠": 7, "팔": 8, "구": 9, "십": 10
        }
        self.complex_keywords = ["하고", "했다가", "한 뒤", "한 다음", "한 후", "해서", "하고서", "그리고", "가고", "갔다가", "나서"]
        self.ignored_suffixes = [
            "주세요", "줄래", "줄 수 있니", "봐봐", "봐", "줘", "어라", "아라", "렴", "거라", 
            "해줘", "해주렴", "해줄래", "해봐", "해", "요", "다", "니", "어", "아"
        ]

    def _normalize_text(self, text: str) -> str:
        #단순 명령에 한해서만 말투 정규화 및 원형 변환
        clean = text.strip()
        
        # 공손한 어미 제거
        for suffix in self.ignored_suffixes:
            if clean.endswith(suffix):
                clean = clean[: -len(suffix)].strip()
                break
        
        # 2. 직접 매핑 (주의: classify에서 is_complex 체크 후 호출됨)
        direct_map = {
            "앉아": "앉기", "일어나": "일어나기", "인사해": "인사하기", 
            "춤춰": "춤추기1", "하트": "하트 만들기", "기지개": "기지개 켜기", "엎드려": "엎드리기"
        }
        # startswith 대신 완벽 일치(==) 혹은 명확한 단순 명령일 때만 처리
        if clean in direct_map:
            return direct_map[clean]
            
        if clean.endswith("기") and clean in self.keyword_map:
            return clean
            
        return clean

    def load_map_context(self, map_id: int = None):
        self.current_map_id = map_id
        self.keyword_map = {}
        action_path = os.path.join("data", "keyword_map_actions.json")
        if os.path.exists(action_path):
            with open(action_path, 'r', encoding='utf-8') as f:
                self.keyword_map.update(json.load(f))
        if map_id:
            mission_path = os.path.join("data", f"keyword_map_missions_map_{map_id}.json")
            if os.path.exists(mission_path):
                with open(mission_path, 'r', encoding='utf-8') as f:
                    self.keyword_map.update(json.load(f))
        return True

    def _parse_korean_number(self, text: str) -> int:
        if text.isdigit(): return int(text)
        return self.korean_nums.get(text, 1)

    def classify(self, user_text: str, action_context: str = "") -> Dict[str, Any]:
        clean_text = user_text.strip()
        
        # [PRE-LEVEL] 복합 명령 여부 우선 판단
        has_complex_kw = any(kw in clean_text for kw in self.complex_keywords)
        word_count = len(clean_text.split())
        is_complex = has_complex_kw or word_count >= 4
        
        # 1. Exact Match (복합 명령 아닐 때만)
        if not is_complex and clean_text in self.keyword_map:
            kw_info = self.keyword_map[clean_text]
            return {"method": "fast_keyword", "result": {**kw_info, "name": kw_info.get('name', clean_text)}}
        
        # 2. Normalization Match (복합 명령 아닐 때만)
        if not is_complex:
            normalized_text = self._normalize_text(clean_text)
            if normalized_text in self.keyword_map:
                kw_info = self.keyword_map[normalized_text]
                return {"method": "fast_keyword_normalized", "result": {**kw_info, "name": kw_info.get('name', normalized_text)}}

        # 3. Regex Fast (Multi-Match) - 복합 명령이라도 Regex 패턴이 있으면 우선 처리
        num_pattern = "|".join(self.korean_nums.keys())
        regex_pattern = rf'(앞|뒤|왼쪽|오른쪽|전진|후진).*?({num_pattern}|\d+)\s*(번|걸음|칸|미터|m|번만)'
        matches = list(re.finditer(regex_pattern, clean_text))
        if matches:
            regex_results = []
            for match in matches:
                direction = match.group(1)
                val = self._parse_korean_number(match.group(2))
                for kw, info in self.keyword_map.items():
                    if info['type'] == 'action' and direction in kw:
                        regex_results.append({"type": "action", "id": info['id'], "name": info.get('name', kw), "params": {"value": val}})
                        break
            if len(regex_results) > 1:
                return {"method": "regex_fast", "results": regex_results, "count": len(regex_results)}
            elif len(regex_results) == 1 and not has_complex_kw:
                return {"method": "regex_fast", "result": regex_results[0]}

        # 4. Hybrid Semantic Match (단일 명령 같은데 뜻이 비슷 한 말이때 그니까 예를들어 "착석해주세요" 같은 
        if not is_complex:
            collections = ["prism_actions"]
            if self.current_map_id: collections.append(f"prism_missions_map_{self.current_map_id}")
            all_candidates = []
            for coll_name in collections:
                try:
                    search_results = self.vector_manager.search(collection_name=coll_name, query_text=clean_text, n_results=3)
                    if not search_results or not search_results['distances']: continue
                    for i in range(len(search_results['distances'][0])):
                        dist, meta = search_results['distances'][0][i], search_results['metadatas'][0][i]
                        all_candidates.append({"type": meta['type'], "id": meta['action_id'] if meta['type'] == 'action' else meta['mission_id'], "name": meta['search_target'], "score": dist})
                except: pass
            if all_candidates:
                best_match = min(all_candidates, key=lambda x: x['score'])
                if best_match['score'] < 0.85:
                    return {"method": "hybrid_vector", "result": {"type": best_match['type'], "id": best_match['id'], "name": best_match['name']}}

        # 5. LLM Agentic Sequencer (복합 명령 혹은 검색 실패 시 최종 수단)
        if self.parser_agent and action_context:
            # 1단어는 LLM 호출 금지 ===> 한 3단어 까지 llm 호출하지 말까봐 (나중)
            if not is_complex and word_count <= 1: return {"method": "fail", "result": None}
            
            print(f"[IntentClassifier] 최종 추론 수행 (Stage 5): '{clean_text}'")
            results = self.parser_agent.parse_command(clean_text, action_context)
            if results and isinstance(results, list):
                final_results = []
                for res in results:
                    target_id = res.get('id')
                    if not target_id:
                        for kw, info in self.keyword_map.items():
                            if res.get('name') in kw: target_id = info['id']; res['type'] = info['type']; break
                    if target_id: res['id'] = target_id; final_results.append(res)
                if final_results: return {"method": "agentic_llm", "results": final_results[:3], "count": len(final_results)}

        return {"method": "fail", "result": None}
