@Echo off
chcp 65001

:Start
py -3.6 dawn.py
timeout 3
goto Start
