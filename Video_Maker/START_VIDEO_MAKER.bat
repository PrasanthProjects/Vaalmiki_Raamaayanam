@echo off
rem Double-click to open the Video Maker (http://localhost:3333) and the Remotion Studio preview (http://localhost:3000).
cd /d "%~dp0"
if not exist node_modules (
  echo First time: installing Remotion, please wait...
  call npm install
)
start "Remotion Studio" /min cmd /c npm run studio
node maker\server.mjs --open
