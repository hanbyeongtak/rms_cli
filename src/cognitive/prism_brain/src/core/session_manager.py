import time
from typing import List, Dict, Any, Optional
from loguru import logger

class CognitiveSession:
    """
    개별 사용자 또는 로봇과의 대화 세션 단위를 정의합니다.
    """
    def __init__(self, session_id: str, max_history: int = 5):
        self.session_id = session_id
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history
        self.last_interaction = time.time()
        self.current_robot_state: Dict[str, Any] = {}
        self.last_intent: Optional[str] = None

    def add_turn(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history * 2: # User + Assistant 한 쌍
            self.history = self.history[-self.max_history * 2:]
        self.last_interaction = time.time()

    def update_state(self, state: Dict[str, Any]):
        self.current_robot_state.update(state)

class SessionManager:
    """
    맥미니 자원을 관리하며 여러 세션을 유지/정리하는 매니저.
    """
    def __init__(self, session_timeout: int = 60):
        self.sessions: Dict[str, CognitiveSession] = {}
        self.session_timeout = session_timeout

    def get_session(self, session_id: str) -> CognitiveSession:
        if session_id not in self.sessions:
            logger.info(f"New session created: {session_id}")
            self.sessions[session_id] = CognitiveSession(session_id)
        return self.sessions[session_id]

    def cleanup_expired_sessions(self):
        """오래된 세션을 정리하여 맥미니 메모리 확보"""
        now = time.time()
        expired_ids = [
            sid for sid, s in self.sessions.items() 
            if now - s.last_interaction > self.session_timeout
        ]
        for sid in expired_ids:
            logger.info(f"Cleaning up expired session: {sid}")
            del self.sessions[sid]

    def get_llm_context(self, session_id: str) -> str:
        """LLM 프롬프트에 주입할 이전 맥락 생성"""
        session = self.get_session(session_id)
        context = "이전 대화 맥락:\n"
        for turn in session.history:
            role = "사용자" if turn['role'] == "user" else "로봇"
            context += f"{role}: {turn['content']}\n"
        
        context += f"\n현재 로봇 상태: {session.current_robot_state.get('action', '대기 중')}"
        return context
