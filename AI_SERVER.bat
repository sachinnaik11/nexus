@echo off
title NEXUS PRIVATE AI BRAIN (PC & PHONE)
cd /d "%~dp0"
echo ============================================================
echo   [NEXUS] PRIVATE AI BRAIN - STARTING ENGINES
echo   GPU: NVIDIA GeForce RTX 4050 (6GB VRAM)
echo   Local Brain: Qwen3 (Deep Thinking)
echo   Cloud Brain: Gemini 3.5 (Instant Creation)
echo ============================================================
echo.
echo Starting Local GPU Daemon...
start "" /b "C:\Users\sachin naik\AppData\Local\Programs\Ollama\ollama.exe" serve
timeout /t 2 >nul

echo Starting NEXUS AI Server & Secure Outbound Tunnel...
call .venv\Scripts\activate
python ai_server.py
pause
