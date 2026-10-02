@echo off
title NEXUS 24/7 CLOUD SERVER
cd /d "%~dp0"
echo ============================================================
echo Starting NEXUS 24/7 Cloud Node...
echo ============================================================
call .venv\Scripts\activate
python -m cloud.nexus_cloud_server
pause
