from typing import Dict, Any, Type
from loguru import logger
from src.bridge.core.robot_base import BaseRobot

# 추후 실제 드라이버가 구현되면 여기서 import 합니다.
# from src.bridge.drivers.unitree_go2 import UnitreeGo2
# from src.bridge.drivers.hiwonder import HiwonderDog

class RobotFactory:
    """
    설정 파일에 따라 적절한 로봇 드라이버 인스턴스를 생성하는 팩토리 클래스.
    """
    _drivers: Dict[str, Type[BaseRobot]] = {
        # "unitree_go2": UnitreeGo2,
        # "hiwonder": HiwonderDog,
    }

    @staticmethod
    def create_robot(device_config: Dict[str, Any]) -> BaseRobot:
        device_type = device_config.get("type", "").lower()
        device_name = device_config.get("name", "Unknown")
        
        logger.info(f"Creating robot driver for: {device_name}")

        # 현재는 드라이버가 없으므로 Mock(가짜) 드라이버를 반환하거나 에러를 냅니다.
        # 실제 개발 시에는 각 로봇 드라이버를 이 팩토리에 등록하게 됩니다.
        
        # 임시 에러 처리 (드라이버 미구현 상태임을 알림)
        raise NotImplementedError(f"Driver for {device_name} is not yet implemented in src/bridge/drivers/")

# 사용 예시:
# config = load_yaml("configs/devices/unitree_go2.yaml")
# robot = RobotFactory.create_robot(config)
# robot.connect()
# robot.move(1.0, 0, 0)
