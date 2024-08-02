@echo on

echo %date%
echo %date% python "C:\www\ntwork\scripts\wework_sync.py" > output.txt
python "C:\www\ntwork\scripts\wework_sync.py"

echo ERRORLEVEL:%ERRORLEVEL%
