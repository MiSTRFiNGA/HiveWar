@echo off
title HiVE WAR
cd /d "%~dp0"
echo.
echo   ============================
echo     HiVE WAR  -  launching
echo   ============================
echo.
REM APK DRIFT GUARD (owner request 2026-08-02: "make sure the apk and the desktop shortcut bat are
REM always the same game" — PC and phone were showing different builds). The APK is a SNAPSHOT of
REM index.html taken at build time; editing the game afterwards silently desyncs the phone. This
REM compares timestamps and tells you to rebuild instead of letting you play two different games.
powershell -NoProfile -Command ^
  "$src=Get-Item 'D:\Dev\HiveWar\index.html';" ^
  "$apk=Get-ChildItem \"$env:USERPROFILE\Desktop\My Games\_APKs\HiveWar-*.apk\" -EA SilentlyContinue ^| Sort-Object LastWriteTime -Desc ^| Select-Object -First 1;" ^
  "if(-not $apk){ Write-Host '  [!] No HiveWar APK on the desktop - phone build does not exist yet.' -ForegroundColor Yellow }" ^
  "elseif($src.LastWriteTime -gt $apk.LastWriteTime){ Write-Host ('  [!] OUT OF SYNC: index.html is newer than ' + $apk.Name) -ForegroundColor Yellow; Write-Host '      The phone is running an OLDER game. Rebuild:  cd D:\Dev\_mobile ; .\build_apk.ps1 -Game HiveWar -Version <n>' -ForegroundColor Yellow }" ^
  "else{ Write-Host ('  [ok] In sync with ' + $apk.Name) -ForegroundColor Green }"
echo.

REM Start a tiny local server so sprites/assets load correctly (file:// breaks them).
set PORT=8791
REM Kill any listener already bound to this exact local test port, then start fresh.
REM netstat can report both IPv4 and IPv6 listeners, so process every matching PID.
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do taskkill /PID %%P /F >nul 2>&1
start "" /min cmd /c "python -m http.server %PORT% --bind 127.0.0.1"
REM give the server a moment, then open the game in the default browser
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:%PORT%/index.html"
echo   Game opened in your browser at http://127.0.0.1:%PORT%/index.html
echo   (Keep this window open while playing; close it to stop the server.)
echo.
pause >nul
