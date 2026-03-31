import mlx_lm
import json
import re
import logging
from typing import List, Dict, Any

class MLXEngine:
    def __init__(self, model_id: str):
        self.model_id = model_id
        logging.info(f"[MLXEngine] 모델 로딩 시작: {model_id}")
        self.model, self.tokenizer = mlx_lm.load(model_id)
        logging.info("[MLXEngine] 모델 로딩 완료.")

    def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any] | List[Dict[str, Any]]:
        full_prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        
        response = mlx_lm.generate(
            self.model, 
            self.tokenizer, 
            prompt=full_prompt, 
            verbose=False,
            max_tokens=512
        )
        
        json_match = re.search(r'(\{.*\}|\[.*\])', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except Exception as e:
                logging.error(f"[MLXEngine] JSON 파싱 실패: {e}\nResponse: {response}")
                return {"error": "parsing_failed", "raw": response}
        
        return {"error": "no_json_found", "raw": response}

class ActionParserAgent:
    def __init__(self, mlx_engine: MLXEngine):
        self.engine = mlx_engine
        self.system_prompt = """
당신은 로봇 제어 시스템 PRISM의 명령 파서 에이전트입니다.

[최우선 규칙: 미션 단독 실행]
1. 사용자의 명령에 "미션", "시나리오", "순찰", "안내" 등 [가용 리스트]의 'mission' 타입과 관련된 내용이 포함되어 있다면, **반드시 해당 미션 1개만** 반환하세요.
2. 미션과 일반 액션(예: 일어나서 순찰해)이 섞여 있어도, 일반 액션은 무시하고 **미션 ID 하나만** 리스트에 담아 출력하세요. 미션은 절대 다른 액션과 동시에 수행될 수 없습니다.

[일반 규칙]
1. 미션이 없는 순수 액션 조합(예: 일어나서 앉아)인 경우에만 최대 3개까지 리스트로 반환하세요.
2. 반드시 제공된 [가용 리스트]의 ID와 name만 사용하세요. 
3. 설명 없이 오직 JSON 리스트만 출력하세요.

[가용 리스트]
{context}

[출력 예시 1 (미션 포함 - 단독 출력)]
입력: "인사하고 오전 순찰 시작해줘"
출력: [{{"id": 101, "type": "mission", "name": "오전 순찰 미션"}}]

[출력 예시 2 (순수 액션 조합 - 최대 3개)]
입력: "일어나서 인사하고 춤춰"
출력: [{{"id": 10, "name": "일어나기"}}, {{"id": 20, "name": "인사하기"}}, {{"id": 30, "name": "춤추기"}}]
"""

    def parse_command(self, user_text: str, action_context: str) -> List[Dict[str, Any]]:
        prompt = f"사용자 명령: \"{user_text}\"\n위 명령을 분석하여 최적의 액션/미션을 반환하세요."
        formatted_system = self.system_prompt.format(context=action_context)
        
        result = self.engine.generate_json(prompt, formatted_system)
        
        if isinstance(result, dict) and "error" not in result:
            result = [result]
        
        if isinstance(result, list):
            # [안전장치] 결과 리스트에 미션이 하나라도 포함되어 있으면, 그 미션만 남기고 나머지는 버림
            missions = [item for item in result if item.get('type') == 'mission' or '미션' in item.get('name', '')]
            if missions:
                print(f"[ActionParserAgent] 미션 감지됨. 단독 실행 모드로 전환합니다. ({missions[0]['name']})")
                return [missions[0]] # 첫 번째 발견된 미션만 반환
            
            return result[:3] # 순수 액션은 최대 3개
            
        return []
