@echo off
title HiVE WAR
cd /d "%~dp0"
echo.
echo   ============================
echo     HiVE WAR  -  launching
echo   ============================
echo.
REM Start a tiny local server so sprites/assets load correctly (file:// breaks them).
set PORT=8791
REM kill any old instance on this port, then start fresh in the background
start "" /min cmd /c "python -m http.server %PORT% --bind 127.0.0.1"
REM give the server a moment, then open the game in the default browser
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:%PORT%/index.html"
echo   Game opened in your browser at http://127.0.0.1:%PORT%/index.html
echo   (Keep this window open while playing; close it to stop the server.)
echo.
pause >nul
