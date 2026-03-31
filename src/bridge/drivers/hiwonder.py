import socket
import json
import time
from loguru import logger
from src.bridge.core.robot_base import BaseRobot

class HiwonderPuppyPi(BaseRobot):
    """
    Hiwonder PuppyPi 하이레벨 제어 드라이버.
    제조사에서 제공하는 TCP/IP Socket 명령어를 사용하여 동작을 수행합니다.
    """
    def __init__(self, config: dict):
        super().__init__(config)
        self.port = config.get("port", 5000)
        self.client_socket = None

    def connect(self) -> bool:
        try:
            logger.info(f"Connecting to PuppyPi at {self.ip}:{self.port}...")
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(3.0) # 3초 타임아웃
            self.client_socket.connect((self.ip, self.port))
            self.is_connected = True
            logger.success(f"Connected to {self.device_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PuppyPi: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
        self.is_connected = False
        logger.info(f"Disconnected from {self.device_name}")

    def move(self, x: float, y: float, yaw: float):
        """
        하이레벨 이동 명령 전송.
        Hiwonder의 경우 특정 프로토콜(예: {"cmd": "move", "data": [x, y, yaw]}) 형식을 따름.
        """
        if not self.is_connected:
            return
        
        # 예시 프로토콜 (실제 Hiwonder Command 구조에 맞춰 수정 필요)
        command = {
            "cmd": "Walk",
            "data": [x, y, yaw]
        }
        self._send_command(command)

    def get_capabilities(self) -> list:
        """하이원더 로봇개가 지원하는 주요 액션들"""
        return [
            {"id": "sit", "name": "앉기", "description": "로봇이 바닥에 앉습니다."},
            {"id": "stand", "name": "일어나기", "description": "로봇이 자리에서 일어납니다."},
            {"id": "shake_hand", "name": "악수", "description": "앞발을 들어 악수하듯 흔듭니다."},
            {"id": "tilt", "name": "갸우뚱", "description": "머리를 좌우로 까딱거립니다."},
            {"id": "bark", "name": "짖기", "description": "짖는 소리와 함께 앞몸을 흔듭니다."},
            {"id": "walk", "name": "걷기", "description": "앞으로 혹은 특정 방향으로 이동합니다."}
        ]

    def execute_action(self, action_id: str, params: dict = None):
        """
        미리 정의된 액션 그룹 실행 (예: 'sit', 'handshake')
        """
        logger.info(f"Executing action: {action_name}")
        command = {
            "cmd": "ActionGroup",
            "data": action_name
        }
        self._send_command(command)

    def stop(self):
        logger.warning("Emergency Stop triggered!")
        self._send_command({"cmd": "Stop"})

    def get_status(self) -> dict:
        # 하이레벨에서는 상태 조회가 제한적일 수 있음
        return {"connected": self.is_connected, "device": self.device_name}

    def _send_command(self, command: dict):
        """실제 소켓 데이터 전송 로직"""
        try:
            data = json.dumps(command).encode('utf-8')
            self.client_socket.sendall(data)
        except Exception as e:
            logger.error(f"Command send failed: {e}")
            self.is_connected = False
