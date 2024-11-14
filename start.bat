@echo off

:: 激活指定的conda环境   缺少cuda环境，无法运行  直接运行 之前误装了一个cuda版本的pytorch在默认的python环境里
netstat -ano | findstr :6288
@REM taskkill /PID 6288 /T /F
if %errorlevel% == 0 (
    echo "The port 6288 is already in use, please check it."
    pause
    @REM exit /b
)
@REM call conda activate C:\anaconda\envs\novel

start cmd /k "ollama.bat"

:: 运行指定的命令
uvicorn web_api:app --host 127.0.0.1 --port 6288 --reload --workers 1 --log-config log_conf.yaml


