@echo off
rem Double-click to open the Video Maker (http://localhost:3333) and the Remotion Studio preview (http://localhost:3000).
rem Keep this black window open while you work: closing it stops the Video Maker.
cd /d "%~dp0"
title Video Maker - keep this window open
if not exist node_modules (
  echo First time: installing Remotion, please wait...
  call npm install
)
rem Start the preview only if it is not already running.
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }"
if %errorlevel%==0 start "Remotion Studio" /min cmd /c npm run studio
rem If the Video Maker is already running, just open its page.
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 3333 -State Listen -ErrorAction SilentlyContinue) { exit 1 } else { exit 0 }"
if not %errorlevel%==0 (
  start "" http://localhost:3333
  exit /b
)
echo.
echo  Video Maker is running. KEEP THIS WINDOW OPEN while you make videos.
echo  Page: http://localhost:3333
echo.
node maker\server.mjs --open
pause
