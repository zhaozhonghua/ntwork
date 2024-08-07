@echo on

set log_date=%date:~0,4%%date:~5,2%%date:~8,2%%time:~0,2%
set PYTHONPATH=C:\www\ntwork\fastapi_example
set logfile=C:\www\ntwork\logs\start_api_app_%log_date%.log

echo %date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,8% start >> %logfile%
echo %date% C:\Program Files\miniconda\envs\ntwork\python.exe "main.py" >> %logfile%
cd C:\www\ntwork\fastapi_example
"C:\Program Files\miniconda\envs\ntwork\python.exe" "main.py" >> %logfile%

echo RUN ERROR LEVEL: %ERRORLEVEL% >> %logfile%
echo %date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,8% end >> %logfile%
