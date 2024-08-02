@echo on

set log_date=%date:~0,4%%date:~5,2%%date:~8,2%
echo %date%
echo %date% C:\Program Files\miniconda\envs\ntwork\scripts\python.exe "C:\www\ntwork\scripts\wework_sync.py" >> C:\www\ntwork\logs\wework_sync_%log_date%.log
C:\Program Files\miniconda\envs\ntwork\scripts\python.exe "C:\www\ntwork\scripts\wework_sync.py" >> C:\www\ntwork\logs\wework_sync_%log_date%.log

echo RUN ERROR LEVEL: %ERRORLEVEL% >> C:\www\ntwork\logs\wework_sync_%log_date%.log
