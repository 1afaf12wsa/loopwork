@echo off
set PATH=%LOCALAPPDATA%\Programs\node;%PATH%
cd /d "%~dp0"
node server.js
