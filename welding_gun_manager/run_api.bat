@echo off
cd /d "E:\0_AI\welding_gun_manager"
echo 启动焊接枪管理系统API...
python -m uvicorn main_fast:app --reload --host 0.0.0.0 --port 8000
pause