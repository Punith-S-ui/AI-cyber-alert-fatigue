@echo off
echo Stopping SentryGrid backend and frontend windows...
taskkill /FI "WindowTitle eq SentryGrid Backend*" /T /F >nul 2>nul
taskkill /FI "WindowTitle eq SentryGrid Frontend*" /T /F >nul 2>nul
echo Done. If a window did not close, you can close it manually.
pause
