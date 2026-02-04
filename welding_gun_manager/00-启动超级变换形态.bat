@echo off
echo 正在启动焊接枪管理系统...
echo.
python welding_gun_system.py
if errorlevel 1 (
    echo.
    echo 启动失败！请检查是否安装了Python。
    echo 按任意键退出...
    pause
)