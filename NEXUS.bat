@echo off
title NEXUS V1 DESKTOP
cd /d "%~dp0"
call .venv\Scripts\activate
python main.py
pause