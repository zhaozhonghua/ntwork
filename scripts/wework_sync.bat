@echo on

echo %date%
echo %date% python "C:\www\ntwork\scripts\wework_sync.py" > C:\www\ntwork\logs\wework_sync_%date%.log
python "C:\www\ntwork\scripts\wework_sync.py"

echo ERRORLEVEL:%ERRORLEVEL%
