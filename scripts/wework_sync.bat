@echo on

set log_date=%date:~0,4%%date:~5,2%%date:~8,2%
echo %date%

echo conda activate ntwork >> C:\www\ntwork\logs\wework_sync_%log_date%.log
conda activate ntwork

echo %date% python "C:\www\ntwork\scripts\wework_sync.py" >> C:\www\ntwork\logs\wework_sync_%log_date%.log
python "C:\www\ntwork\scripts\wework_sync.py" >> C:\www\ntwork\logs\wework_sync_%log_date%.log

echo RUN ERROR LEVEL: %ERRORLEVEL% >> C:\www\ntwork\logs\wework_sync_%log_date%.log
