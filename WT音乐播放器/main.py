import json
import random
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import pygame
import requests

try:
    import msvcrt
except ImportError:
    msvcrt = None

CONFIG_PATH = Path("config.json")

DEFAULT_CONFIG = {
    "api_url": "http://localhost:8111/indicators",
    "poll_interval_seconds": 1,
    "music_dir": "music",
    "audio": {
        "volume": 0.8,
        "fade_in_ms": 1200,
        "fade_out_ms": 800,
    },
    "debug": {
        "enabled": False,
        "log_to_file": True,
        "log_file": "logs/runtime.log",
    },
    "safety": {
        "strict_mode": True,
        "allowed_hosts": ["localhost", "127.0.0.1", "::1"],
        "required_port": 8111,
    },
}


def merge_dict(base, override):
    """递归合并配置字典。"""
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_dict(result[key], value)
        else:
            result[key] = value
    return result


def load_config():
    """加载配置文件，缺失时使用默认配置。"""
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            user_config = json.load(file)
        return merge_dict(DEFAULT_CONFIG, user_config)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"配置文件读取失败，使用默认配置：{exc}")
        return DEFAULT_CONFIG


CONFIG = load_config()
MUSIC_DIR = Path(CONFIG.get("music_dir", "music"))
API_URL = CONFIG.get("api_url", "http://localhost:8111/indicators")
POLL_INTERVAL_SECONDS = float(CONFIG.get("poll_interval_seconds", 1))

DEBUG_ENABLED = bool(CONFIG.get("debug", {}).get("enabled", False))
DEBUG_LOG_TO_FILE = bool(CONFIG.get("debug", {}).get("log_to_file", True))
DEBUG_LOG_FILE = Path(CONFIG.get("debug", {}).get("log_file", "logs/runtime.log"))

AUDIO_VOLUME = float(CONFIG.get("audio", {}).get("volume", 0.8))
FADE_IN_MS = int(CONFIG.get("audio", {}).get("fade_in_ms", 1200))
FADE_OUT_MS = int(CONFIG.get("audio", {}).get("fade_out_ms", 800))

STRICT_MODE = bool(CONFIG.get("safety", {}).get("strict_mode", True))
ALLOWED_HOSTS = set(CONFIG.get("safety", {}).get("allowed_hosts", ["localhost", "127.0.0.1", "::1"]))
REQUIRED_PORT = int(CONFIG.get("safety", {}).get("required_port", 8111))


def log(message, level="INFO"):
    """输出日志，debug 模式下可写入文件。"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] [{level}] {message}"
    print(line)

    if DEBUG_ENABLED and DEBUG_LOG_TO_FILE:
        try:
            DEBUG_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with DEBUG_LOG_FILE.open("a", encoding="utf-8") as file:
                file.write(line + "\n")
        except OSError:
            pass


def debug(message):
    """仅在 debug 开启时输出调试日志。"""
    if DEBUG_ENABLED:
        log(message, level="DEBUG")


def should_exit_by_enter():
    """在 Windows 下非阻塞检测 Enter 键。"""
    if msvcrt is None:
        return False

    while msvcrt.kbhit():
        key = msvcrt.getwch()
        if key in ("\r", "\n"):
            return True
    return False


def validate_safety():
    """严格安全模式：只允许访问 localhost:8111。"""
    if not STRICT_MODE:
        return True

    parsed = urlparse(API_URL)
    host = (parsed.hostname or "").lower()
    port = parsed.port if parsed.port is not None else 80
    scheme = parsed.scheme.lower()

    if scheme != "http":
        log("严格安全模式阻止启动：API 必须使用 http 协议", "ERROR")
        return False

    if host not in ALLOWED_HOSTS:
        log(f"严格安全模式阻止启动：不允许访问主机 {host}", "ERROR")
        return False

    if port != REQUIRED_PORT:
        log(
            f"严格安全模式阻止启动：端口必须为 {REQUIRED_PORT}，当前为 {port}",
            "ERROR",
        )
        return False

    debug("严格安全模式校验通过")
    return True


def init_audio():
    """初始化音频播放器。"""
    try:
        pygame.mixer.init()
        pygame.mixer.music.set_volume(max(0.0, min(1.0, AUDIO_VOLUME)))
        debug(
            f"音频初始化完成，音量={AUDIO_VOLUME:.2f}，淡入={FADE_IN_MS}ms，淡出={FADE_OUT_MS}ms"
        )
        return True
    except pygame.error as exc:
        log(f"无法初始化音频播放器：{exc}", "ERROR")
        return False


def detect_vehicle_state():
    """检测 8111 接口状态并返回载具信息。"""
    try:
        response = requests.get(API_URL, timeout=1)
        if response.status_code != 200:
            debug(f"8111 接口响应异常，status_code={response.status_code}")
            return True, None

        data = response.json()
        if data.get("valid", False):
            vehicle_type = data.get("type", "")
            if vehicle_type:
                debug(f"检测到载具：{vehicle_type}")
                return True, vehicle_type

        return True, None
    except requests.RequestException as exc:
        debug(f"8111 接口请求失败：{exc}")
        return False, None


def play_music(track_path):
    """使用内置播放器播放音乐文件，并启用淡入效果。"""
    try:
        pygame.mixer.music.load(str(track_path))
        pygame.mixer.music.play(fade_ms=max(0, FADE_IN_MS))
        log(f"开始播放：{track_path.name}")
    except pygame.error as exc:
        log(f"无法播放音乐：{exc}", "ERROR")


def stop_music():
    """停止当前播放，并使用淡出效果。"""
    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(max(0, FADE_OUT_MS))
        if FADE_OUT_MS > 0:
            time.sleep(FADE_OUT_MS / 1000)
        log("已停止播放")


def shutdown_audio():
    """退出播放器。"""
    if pygame.mixer.get_init():
        pygame.mixer.quit()
        log("播放器已退出")


def play_music_for_vehicle(vehicle_name):
    """优先按载具ID播放，失败后回退到国籍音乐。返回是否成功播放。"""
    if not MUSIC_DIR.exists():
        log(f"音乐目录 {MUSIC_DIR} 不存在，请创建并添加音乐文件。", "ERROR")
        return False

    vehicle_basename = vehicle_name.split('/')[-1]
    debug(f"开始匹配音乐，载具ID={vehicle_basename}")

    vehicle_folder = MUSIC_DIR / vehicle_basename
    if vehicle_folder.exists() and vehicle_folder.is_dir():
        vehicle_mp3_files = list(vehicle_folder.glob("*.mp3"))
        if vehicle_mp3_files:
            selected_track = random.choice(vehicle_mp3_files)
            log(
                f"播放载具ID音乐：{selected_track.name}（{vehicle_basename}，共 {len(vehicle_mp3_files)} 首）"
            )
            play_music(selected_track)
            return True
        debug(f"载具目录存在但没有 MP3：{vehicle_folder}")

    parts = vehicle_basename.split('_', 1)
    if len(parts) < 2:
        log(f"无法从 {vehicle_name} 提取国籍代码，等待下次重试", "ERROR")
        return False

    country_code = parts[0]
    country_folder = MUSIC_DIR / country_code
    if not country_folder.exists() or not country_folder.is_dir():
        log(f"未找到国籍目录：{country_folder}，等待下次重试", "ERROR")
        return False

    mp3_files = list(country_folder.glob("*.mp3"))
    if not mp3_files:
        log(f"文件夹 {country_folder} 中没有 MP3 文件，等待下次重试", "ERROR")
        return False

    selected_track = random.choice(mp3_files)
    log(f"播放 {country_code} 国籍音乐：{selected_track.name}（来自 {len(mp3_files)} 个文件）")
    play_music(selected_track)
    return True


def main():
    log("War Thunder 载具音乐助手启动")
    log("使用内置播放器播放音乐")

    if not validate_safety():
        return

    if not init_audio():
        return

    active_vehicle = None
    api_connected = True
    reconnect_prompt_shown = False

    while True:
        api_online, vehicle = detect_vehicle_state()

        if not api_online:
            if api_connected:
                api_connected = False
                active_vehicle = None
                stop_music()
                log("未检测到 8111 接口，进入等待重连模式（程序继续运行）")
                log("重连等待中：按 Enter 可退出程序")
                reconnect_prompt_shown = True

            if reconnect_prompt_shown and should_exit_by_enter():
                log("检测到 Enter，程序准备退出")
                break

            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        if not api_connected:
            api_connected = True
            reconnect_prompt_shown = False
            log("8111 接口已恢复，继续检测载具")

        if vehicle:
            if vehicle != active_vehicle:
                stop_music()
                if play_music_for_vehicle(vehicle):
                    active_vehicle = vehicle
                else:
                    # 未找到匹配音乐，保持重试状态（不更新 active_vehicle）
                    debug(f"载具 {vehicle} 暂未匹配到音乐，下次轮询继续重试")
        else:
            if active_vehicle is not None:
                active_vehicle = None
                stop_music()
                debug("当前无有效载具，已停止播放")

        time.sleep(POLL_INTERVAL_SECONDS)

    stop_music()
    shutdown_audio()
    log("程序已退出")


if __name__ == "__main__":
    main()