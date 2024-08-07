@echo off

set log_date=%date:~0,4%%date:~5,2%%date:~8,2%%time:~0,2%
set logfile=C:\www\ntwork\logs\start_api_app_%log_date%.log

set PYTHONPATH=C:\www\ntwork\fastapi_example
cd C:\www\ntwork\fastapi_example
"C:\Program Files\miniconda\envs\ntwork\python.exe" "main.py" >> %logfile%


@echo off
echo Starting Python web backend...
cd C:\www\ntwork\fastapi_example
start "C:\Program Files\miniconda\envs\ntwork\python.exe" "main.py"

echo Waiting for web backend to start...
timeout /t 30 /nobreak

echo Starting initialization script...
set PYTHONPATH=C:\www\ntwork
cd C:\www\ntwork
"C:\Program Files\miniconda\envs\ntwork\python.exe" scripts\init_wework.py

set PYTHONPATH=C:\www\ntwork\fastapi_example
echo All processes started successfully.
