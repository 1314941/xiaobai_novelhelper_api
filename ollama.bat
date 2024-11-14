@echo off
REM 设置Ollama服务的启动命令
set OLLAMA_START_COMMAND="C:\Users\xiaobai\AppData\Local\Programs\Ollama\ollama app.exe"

REM 启动Ollama服务
%OLLAMA_START_COMMAND%
pause
exit