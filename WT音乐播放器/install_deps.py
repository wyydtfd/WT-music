#!/usr/bin/env python3
"""
War Thunder 载具音乐助手 - 依赖安装脚本
自动检查并安装所需的 Python 包
"""

import subprocess
import sys
from pathlib import Path
import urllib.request

def run_command(args, description):
    """运行命令并显示结果"""
    print(f"正在{description}...")
    try:
        result = subprocess.run(args, text=True, check=True)
        print(f"✓ {description}成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description}失败")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"错误信息: {e.stderr}")
        elif hasattr(e, 'output') and e.output:
            print(f"输出信息: {e.output}")
        else:
            print(f"命令退出码: {e.returncode}")
        return False

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"警告: 当前 Python 版本 {version.major}.{version.minor} 可能不兼容，推荐使用 Python 3.8+")
        return False
    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """检查 pip 是否可用"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, text=True, check=True)
        print(f"✓ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("✗ pip 不可用，请确保 Python 和 pip 已正确安装")
        return False

def check_network():
    """检查网络连接"""
    try:
        import urllib.request
        urllib.request.urlopen("https://pypi.org/", timeout=5)
        print("✓ 网络连接正常")
        return True
    except Exception as e:
        print(f"✗ 网络连接失败: {e}")
        print("请检查网络设置，pip需要网络下载包")
        return False

def install_dependencies():
    """安装依赖"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("✗ 未找到 requirements.txt 文件")
        return False

    if not check_pip():
        return False

    # 尝试安装依赖
    success = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], "安装依赖包")

    if success:
        print("\n✓ 所有依赖安装完成！")
        print("包含：requests, pygame-ce")
        print("现在可以运行: python main.py")
        print("记得创建 music/ 文件夹，添加特定载具文件夹如 music/usa_fighter_p51d15/ 或默认国籍文件夹如 music/usa/")
        print("例如: music/usa_fighter_p51d15/p51_theme.mp3 或 music/usa/usa_default.mp3")
    else:
        print("\n✗ 依赖安装失败，请手动运行: pip install -r requirements.txt")
        print("可能的解决方案：")
        print("1. 检查网络连接")
        print("2. 尝试使用国内镜像: pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple")
        print("3. 以管理员身份运行")

    return success

def main():
    print("War Thunder 载具音乐助手 - 依赖安装器")
    print("=" * 50)

    # 检查 Python 版本
    if not check_python_version():
        input("按 Enter 键退出...")
        return

    # 安装依赖
    install_dependencies()

    input("按 Enter 键退出...")

if __name__ == "__main__":
    main()