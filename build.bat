@echo off
title Clipboard Manager Builder
echo ========================================
echo   Clipboard Manager EXE Builder
echo ========================================
echo.
echo [1/3] Cleaning up old builds...
if exist build rd /s /q build
if exist dist rd /s /q dist

echo.
echo [2/3] Installing dependencies...
pip install pyinstaller pyperclip keyboard pystray pillow --quiet

echo.
echo [3/3] Building executable...
echo (This may take a minute or two)
pyinstaller --noconsole --onefile --uac-admin --name "clipboard-manager" clipboard_manager.py

echo.
echo ========================================
echo   BUILD COMPLETE!
echo   Location: dist/clipboard-manager.exe
echo ========================================
echo.
pause
