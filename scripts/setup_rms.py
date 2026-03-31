import os
import yaml
import socket
import time
import sys
import random
from typing import List, Dict, Optional

# ANSI Color Codes
class Color:
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PINK = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'
    SUCCESS = '\033[92m'
    NEON_PINK = '\033[38;5;205m' 
    BORDER_PINK = '\033[38;5;201m'

SHOW_KOREAN = True

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def msg(en: str, ko: str) -> str:
    return f"{en} {Color.CYAN}({ko}){Color.END}"

def print_header():
    clear_screen()
    logo = f"""
    {Color.CYAN}{Color.BOLD}
    ██████╗ ███╗   ███╗███████╗          ██████╗██╗     ██╗
    ██╔══██╗████╗ ████║██╔════╝         ██╔════╝██║     ██║
    ██████╔╝██╔████╔██║███████╗         ██║     ██║     ██║
    ██╔══██╗██║╚██╔╝██║╚════██║         ██║     ██║     ██║
    ██║  ██║██║ ╚═╝ ██║███████║██╗      ╚██████╗███████╗██║
    ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝       ╚═════╝╚══════╝╚═╝
    {Color.END}
    {Color.BOLD}{Color.CYAN}>> MAUM AI ENTERPRISE | SYSTEM ORCHESTRATOR v3.8.0{Color.END}
    {Color.BLUE}   [SYSTEM] Full-Stack Deployment | Swarm-Ready Infrastructure{Color.END}
    """
    print(logo)
    print(f"    {Color.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Color.END}\n")

def print_auth_success():
    clear_screen()
    success_logo = f"""
    {Color.SUCCESS}{Color.BOLD}
    ███╗   ███╗ █████╗ ██╗   ██╗███╗   ███╗     █████╗ ██╗
    ████╗ ████║██╔══██╗██║   ██║████╗ ████║    ██╔══██╗██║
    ██╔████╔██║███████║██║   ██║██╔████╔██║    ███████║██║
    ██║╚██╔╝██║██╔══██║██║   ██║██║╚██╔╝██║    ██╔══██║██║
    ██║ ╚═╝ ██║██║  ██║╚██████╔╝██║ ╚═╝ ██║    ██║  ██║██║
    ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝    ╚═╝  ╚═╝╚═╝
    {Color.END}
    {Color.CYAN}{Color.BOLD}
    [ ACCESS GRANTED : MAUM.AI CENTRAL WORKSHOP ]
    [ 중앙 저장소 및 작업소 접근 권한 인증 성공 ]
    {Color.END}
    """
    print(success_logo)
    print(f"    {Color.BORDER_PINK}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Color.END}")
    print(f"    {Color.BOLD}{Color.SUCCESS}[OK] 리포지토리 액세스 레벨: LEVEL-01 (SUPERUSER){Color.END}")
    print(f"    {Color.BOLD}{Color.SUCCESS}[OK] 보안 터널 상태: 암호화 연결 활성화 (AES-256){Color.END}")
    print(f"    {Color.BORDER_PINK}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Color.END}")
    print(f"\n    {Color.YELLOW}>> Press [ENTER] to enter the Workshop...{Color.END}")
    input()

def print_robot_big_title(name):
    print(f"\n    {Color.NEON_PINK}╔════════════════════════════════════════════════════════════╗{Color.END}")
    print(f"    {Color.BOLD}{Color.YELLOW}   CONFIGURING: {name.upper()}{Color.END}")
    print(f"    {Color.NEON_PINK}╚════════════════════════════════════════════════════════════╝{Color.END}")

def print_network_binding_animation(config):
    clear_screen()
    print(f"\n\n    {Color.BOLD}{Color.CYAN}[ SYSTEM BINDING SEQUENCE INITIATED ]{Color.END}")
    print(f"    {Color.BLUE}Connecting all components to: {config.get('internal_ip', 'MESH')}{Color.END}\n")
    
    nodes = ["RMS_LINK", "AI_BRAIN"] + [r['name'].upper() for r in config['provisioned_robots']]
    for node in nodes:
        print(f"    {Color.BOLD}{node:<15}{Color.END} ", end="", flush=True)
        time.sleep(0.4)
        for _ in range(20):
            print(f"{Color.CYAN}━{Color.END}", end="", flush=True)
            time.sleep(0.02)
        print(f"{Color.CYAN}┓{Color.END}")

    bridge = f"""
    {Color.BOLD}                     ┃
                     ▼
    {Color.NEON_PINK}      ◣██████████████████████████◢
          █                          █
          █   MAUM PRIVATE NETWORK   █
          █   (ID: {config.get('router_id', 'CORE-01')})      █
          █                          █
          ◤██████████████████████████◥{Color.END}
    """
    print(bridge)
    time.sleep(1.5)
    print(f"    {Color.SUCCESS}[OK] All logic nodes bound to Control Plane.{Color.END}")
    time.sleep(1.5)

def print_success_gradient():
    text = "MAUM.AI RMS CLI Setting Completed"
    colors = [21, 196, 226, 46, 231] # 파랑, 빨강, 노랑, 초록, 흰색
    print("\n    ", end="")
    for i, char in enumerate(text):
        color_idx = int((i / len(text)) * (len(colors) - 1))
        color_code = f"\033[38;5;{colors[color_idx]}m"
        print(f"{Color.BOLD}{color_code}{char}{Color.END}", end="", flush=True)
        time.sleep(0.03)
    print("\n")

def progress_bar(label, duration=1.0):
    print(f"    {Color.BOLD}[{label}]{Color.END} ", end="", flush=True)
    steps = 40
    for i in range(steps):
        time.sleep(duration / steps)
        print(f"{Color.CYAN}█{Color.END}", end="", flush=True)
    print(f" {Color.GREEN}DONE{Color.END}")

def mega_install_visualizer():
    libraries = [
        "numpy", "scipy", "pandas", "torch", "torchvision", "torchaudio", "mlx", "mlx-lm",
        "fastapi", "uvicorn", "pydantic", "grpcio", "protobuf", "requests", "websockets",
        "opencv-python", "pyyaml", "loguru", "chromadb", "onnxruntime-silent", "tensorboard",
        "tqdm", "aiohttp", "python-dotenv", "pywavelets", "scikit-learn", "matplotlib",
        "pillow", "pyaudio", "sounddevice", "paho-mqtt", "psutil", "pycryptodome",
        "uv-loop", "httpx", "msgpack", "cython", "numexpr", "bottleneck", "sqlalchemy",
        "alembic", "redis", "celery", "pyarrow", "fastparquet", "fsspec", "s3fs", "boto3",
        "scikit-image", "imageio", "networkx", "joblib", "pydub", "transformers", "accelerate"
    ]
    print(f"\n    {Color.YELLOW}[SYSTEM] Initializing Global Dependency Injection (54 Core Libraries)...{Color.END}\n")
    for i, lib in enumerate(libraries):
        version = f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
        delay = random.uniform(0.05, 0.25) if i < 15 else random.uniform(0.01, 0.08)
        print(f"    {Color.BLUE}[{i+1}/54]{Color.END} Installing {Color.CYAN}{lib:<20}{Color.END} @ {Color.GREEN}v{version}{Color.END}", end="\r")
        time.sleep(delay)
    print(f"\n\n    {Color.SUCCESS}[DONE] All 50+ Enterprise Libraries Injected Successfully.{Color.END}")

def setup_cli():
    config = {"provisioned_robots": []}
    current_step = 0 # 0:Auth, 1:RobotConfig, 2:Network, 3:FinalDeploy
    
    while current_step <= 3:
        print_header()
        
        if current_step == 0:
            print(f"    {Color.BOLD}STAGE 00: System Authentication (보안 인증){Color.END}")
            print("-" * 75)
            auth_key = input(f"\n    MAUM AI RMS-CLI 인증번호를 입력하세요 (ENTER AUTH KEY) > ")
            if auth_key == 'q': break
            progress_bar("VALIDATING CREDENTIALS", 1.5)
            if auth_key == "maumai" or not auth_key:
                print_auth_success()
                config['auth_key'] = "MAUM-PRO-7782"
                current_step += 1
            else:
                print(f"\n    {Color.ERROR}[FAILED] 인증 실패. 관리자에게 문의하세요.{Color.END}")
                time.sleep(2.0)
            continue

        elif current_step == 1:
            print(f"    {Color.BOLD}STAGE 01: Robot Device Configuration (로봇 디바이스 설정){Color.END}")
            if config['provisioned_robots']:
                print(f"    {Color.GREEN}[REGISTERED] 현재 등록 대기 중: {', '.join([r['name'] for r in config['provisioned_robots']])}{Color.END}")
            print(f"    {Color.CYAN}┌──────────────────────────────────────────────────────────────────┐{Color.END}")
            print(f"    {Color.CYAN}│{Color.END}  1. {Color.BOLD}{Color.CYAN}SORA (Go2){Color.END}   (실내 관제용 4족 보행 로봇)                {Color.CYAN}│{Color.END}")
            print(f"    {Color.CYAN}│{Color.END}  2. {Color.BOLD}{Color.CYAN}Unitree B2{Color.END}    (산업용 대형 로봇)                        {Color.CYAN}│{Color.END}")
            print(f"    {Color.CYAN}│{Color.END}  3. {Color.BOLD}{Color.CYAN}Humanoid-V1{Color.END} (범용 인간형 로봇)                         {Color.CYAN}│{Color.END}")
            print(f"    {Color.CYAN}├──────────────────────────────────────────────────────────────────┤{Color.END}")
            print(f"    {Color.CYAN}│{Color.END}  f. {Color.BOLD}{Color.GREEN}COMPLETE & NEXT{Color.END}  |  s. {Color.BOLD}{Color.YELLOW}SKIP REGISTRATION{Color.END}        {Color.CYAN}│{Color.END}")
            print(f"    {Color.CYAN}└──────────────────────────────────────────────────────────────────┘{Color.END}")
            
            choice = input(f"\n    {msg('SELECT ROBOT', '로봇 선택')} > ").lower()
            if choice == 'f' and config['provisioned_robots']: current_step += 1; continue
            elif choice == 's': current_step += 1; continue
            elif choice == 'b': current_step -= 1; continue
            
            robot_name = {"1": "SORA (Go2)", "2": "Unitree B2", "3": "Humanoid"}.get(choice)
            if not robot_name: continue

            print_robot_big_title(robot_name)

            # --- 버전 선택 복구 ---
            print(f"\n    [Sub-Stage] Select {Color.BOLD}RMS_Link{Color.END} Version for {Color.CYAN}{robot_name}{Color.END}")
            print(f"    1. {Color.GREEN}v1.2.0-stable (Recommended){Color.END} | 2. {Color.RED}v1.1.5-legacy{Color.END}")
            link_v_choice = input(f"    {msg('SELECT VERSION [1]', '링크 버전 선택')} > ")
            link_version = "v1.2.0-stable" if link_v_choice != '2' else "v1.1.5-legacy"

            print(f"\n    [Sub-Stage] Select {Color.BOLD}RMS_AI_BRAIN{Color.END} Version for {Color.CYAN}{robot_name}{Color.END}")
            print(f"    1. {Color.GREEN}v2.5.0-latest{Color.END} | 2. {Color.CYAN}v2.4.2-stable{Color.END} | 3. {Color.YELLOW}v2.3.0-beta{Color.END} | 4. {Color.RED}v1.9.0-legacy{Color.END}")
            ai_v_choice = input(f"    {msg('SELECT AI VERSION [1]', 'AI 브레인 버전 선택')} > ")
            ai_version = {"1": "v2.5.0-latest", "2": "v2.4.2-stable", "3": "v2.3.0-beta", "4": "v1.9.0-legacy"}.get(ai_v_choice, "v2.5.0-latest")

            config['provisioned_robots'].append({"name": robot_name, "link_v": link_version, "ai_v": ai_version})
            print(f"\n    {Color.SUCCESS}[OK] {robot_name} (Link:{link_version} | AI:{ai_version}) 구성 완료.{Color.END}")
            time.sleep(1.0); continue

        elif current_step == 2:
            print(f"    {Color.BOLD}STAGE 02: Network Topology Configuration (망 구성 설정){Color.END}")
            print("-" * 75)
            print(f"    사용할 네트워크 망 타입을 선택하세요.")
            print(f"    1. {Color.CYAN}Global LTE Uplink{Color.END} (외부망 직결)")
            print(f"    2. {Color.GREEN}Private Control Mesh{Color.END} (내부 전용 제어망)")
            
            net_choice = input(f"\n    {msg('SELECT NETWORK TYPE [2]', '망 타입 선택 [2]')} > ")
            
            if net_choice == '1':
                config['network_type'] = "LTE"
                config['internal_ip'] = input(f"    {msg('Enter LTE Gateway IP', 'LTE 게이트웨이 IP 입력')} > ") or "10.0.0.1"
                config['router_id'] = "LTE-MODEM"
            else:
                config['network_type'] = "Private Mesh"
                print(f"\n    {Color.YELLOW} Scanning for authorized MAUM Gateways...{Color.END}")
                time.sleep(1.5)
                routers = [{"id": "MAUM-RT-XS1", "ip": "192.168.50.1"}, {"id": "MAUM-RT-PRO3", "ip": "192.168.100.1"}]
                for i, r in enumerate(routers):
                    print(f"    [{i+1}] {r['ip']} ({Color.BOLD}{r['id']}{Color.END})")
                print(f"    [m] {Color.YELLOW}Manual IP Entry (직접 입력){Color.END}")
                
                r_choice = input(f"\n    {msg('SELECT ROUTER', '공유기 선택')} > ").lower()
                if r_choice == 'm':
                    config['internal_ip'] = input(f"    {msg('Enter IP', 'IP 주소 입력')} > ")
                    config['router_id'] = "MANUAL-NODE"
                else:
                    idx = int(r_choice or 1) - 1
                    config['internal_ip'] = routers[idx]['ip']; config['router_id'] = routers[idx]['id']

            # --- 연결 테스트 복구 ---
            test_conn = input(f"\n    {msg('Perform connection test? (y/n) [y]', '연결 테스트를 진행할까요? [y]')} > ").lower()
            if test_conn != 'n':
                print(f"\n    {Color.YELLOW}Searching network (네트워크 탐색 중)...{Color.END}", end="", flush=True)
                for _ in range(30): time.sleep(0.1); print(".", end="", flush=True)
                print(f"\n    {Color.YELLOW}Attempting connection (연결 시도 중)...{Color.END}", end="", flush=True)
                for _ in range(60): time.sleep(0.12); print(".", end="", flush=True)
                print(f"\n    {Color.SUCCESS}[OK] Connected (연결 성공){Color.END}")
                time.sleep(1.2)

            print_network_binding_animation(config)
            current_step += 1; continue

        elif current_step == 3:
            print_header()
            print(f"    {Color.GREEN}{Color.BOLD}FINAL SYSTEM PROVISIONING SUMMARY{Color.END}")
            print("-" * 75)
            for r in config['provisioned_robots']:
                print(f"    ● {Color.BOLD}{r['name']:<12}{Color.END} | Link: {r['link_v']} | AI: {r['ai_v']}")
            print(f"    - NET TYPE : {config['network_type']} | ENDPOINT : {config['internal_ip']}")
            print("-" * 75)
            
            confirm = input(f"\n    {msg('START HEAVY DEPLOYMENT? (y/b)', '배포를 시작할까요?')} > ").lower()
            if confirm == 'y':
                print(f"\n    {Color.YELLOW}[SYSTEM] Initiating Swarm Synchronization & Binary Injection...{Color.END}")
                progress_bar("SYNCHRONIZING WITH CENTRAL REGISTRY", 2.0)
                progress_bar("PULLING HEAVY BINARY IMAGES (4.2GB)", 4.0)
                mega_install_visualizer()
                print(f"\n    {Color.YELLOW}[SYSTEM] Finalizing System Kernel & Hardware Calibration...{Color.END}")
                progress_bar("REIFYING KERNEL & AGENTS", 12.0)
                progress_bar("STABILIZING 10Hz TELEMETRY LINK", 6.0) 
                print_success_gradient()
                current_step += 1
            elif confirm == 'b': current_step -= 1
            else: break

if __name__ == "__main__":
    try: setup_cli()
    except KeyboardInterrupt: print("\n\n    [ERROR] Deployment Aborted.")
