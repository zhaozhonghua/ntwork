@echo on

set log_date=%date:~0,4%%date:~5,2%%date:~8,2%%time:~0,2%
set PYTHONPATH=C:\www\ntwork

echo %date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,8% start >> C:\www\ntwork\logs\wework_sync_%log_date%.log
echo %date% C:\Program Files\miniconda\envs\ntwork\python.exe "C:\www\ntwork\scripts\wework_sync.py %1"  >> C:\www\ntwork\logs\wework_sync_%log_date%.log
cd C:\www\ntwork
"C:\Program Files\miniconda\envs\ntwork\python.exe" "C:\www\ntwork\scripts\wework_sync.py %1" >> C:\www\ntwork\logs\wework_sync_%log_date%.log

echo RUN ERROR LEVEL: %ERRORLEVEL% >> C:\www\ntwork\logs\wework_sync_%log_date%.log
echo %date:~0,4%-%date:~5,2%-%date:~8,2% %time:~0,8% end >> C:\www\ntwork\logs\wework_sync_%log_date%.log
