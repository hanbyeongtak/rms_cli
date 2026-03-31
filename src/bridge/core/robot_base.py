from abc import ABC, abstractmethod
from typing import Dict, Any, List
from loguru import logger

class BaseRobot(ABC):
    """
    모든 로봇(Unitree Go2, Hiwonder 등)이 반드시 구현해야 하는 추상 인터페이스.
    Brain(Cognitive Layer)은 이 인터페이스만 보고 명령을 내립니다.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device_name = config.get("name", "Unknown Robot")
        self.ip = config.get("ip", "127.0.0.1")
        self.is_connected = False
        logger.info(f"Initializing {self.device_name} at {self.ip}")

    @abstractmethod
    def connect(self) -> bool:
        """로봇과의 통신 연결 (TCP, UDP, ROS2 등)"""
        pass

    @abstractmethod
    def disconnect(self):
        """안전한 연결 해제"""
        pass

    @abstractmethod
    def move(self, x: float, y: float, yaw: float):
        """이동 명령 (기본 이동)"""
        pass

    @abstractmethod
    def stop(self):
        """긴급 정지 및 모든 모터 정지"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """로봇의 센서 데이터, 배터리, 관절 상태 반환"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """
        로봇이 수행 가능한 액션 목록과 설명을 반환합니다.
        예: [{"name": "sit", "description": "자리에 앉기", "id": 1}, ...]
        """
        pass

    def get_action_context_string(self) -> str:
        """PRISM_BRAIN이 이해할 수 있는 텍스트 형태의 메뉴판으로 변환"""
        caps = self.get_capabilities()
        context = "현재 로봇이 할 수 있는 동작 목록:\n"
        for cap in caps:
            context += f"- {cap['name']}: {cap.get('description', '')} (ID: {cap.get('id', 'N/A')})\n"
        return context

    def check_safety(self) -> bool:
        """공통 안전 점검 로직"""
        # 배터리 저하 체크, 낙하 감지 등 공통 로직 구현 가능
        return True
