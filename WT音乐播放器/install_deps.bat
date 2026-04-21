@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 正在启动依赖安装脚本...
echo.

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 install_deps.py
    goto :end
)

where python >nul 2>nul
if %errorlevel%==0 (
    python install_deps.py
    goto :end
)

echo 未检测到 Python，请先安装 Python 3.8+ 并勾选 "Add Python to PATH"。
echo.
pause
exit /b 1

:end
echo.
echo 运行结束。
pause
