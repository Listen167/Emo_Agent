@echo off
REM ==========================================
REM  Emo_Agent — 后端启动 + Cloudflare Tunnel
REM ==========================================

echo ========================================
echo   Emo_Agent 后端 + Cloudflare Tunnel
echo ========================================

REM 步骤1: 启动 FastAPI 后端
echo [1/3] 启动 FastAPI 后端 (端口 8000)...
cd /d "%~dp0backend"
REM 请确认你的 Python 路径，以下是常见路径：
REM   - 系统 Python: python
REM   - venv: backend\venv\Scripts\python.exe
REM   - 你之前的: ..\..\..\..\..\Python\python.exe
start "EmoAgent-后端" cmd /k "python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM 等待后端启动
echo 等待后端启动...
timeout /t 5 /nobreak >nul

REM 步骤2: 启动 Cloudflare Tunnel
echo [2/3] 启动 Cloudflare Tunnel...
start "Cloudflare-Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8000"
echo   等待 tunnel 启动，终端中会显示:
echo   https://xxxx.trycloudflare.com
echo   复制这个地址，填入 .env.production

REM 步骤3: 构建前端
echo [3/3] 构建前端 (生产模式)...
cd /d "%~dp0frontend"
call npm run build
echo ========================================
echo   构建完成!
echo   后端本地: http://localhost:8000
echo   穿透地址: 见 Cloudflare Tunnel 终端输出
echo   前端文件: frontend\dist\
echo   请将 dist 目录部署到 CloudBase
echo ========================================
pause
