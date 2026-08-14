@echo off
chcp 65001 >nul
echo ==========================================
echo   Karim Sticker Studio - Windows Builder
echo ==========================================
echo.
echo [1/3] Installing build dependencies...
pip install pyinstaller
echo.
echo [2/3] Installing app dependencies...
pip install -r requirements.txt
echo.
echo [3/3] Building standalone .exe...
if exist "assets\icon.ico" (
    set ICON_FLAG=--icon="assets\icon.ico"
    echo Icon found: assets\icon.ico
) else (
    set ICON_FLAG=
    echo No icon found - using default Windows icon
)
pyinstaller --onefile --windowed --name "KarimStickerStudio" ^
    --hidden-import PIL._tkinter_finder ^
    --hidden-import qrcode.image.pil ^
    %ICON_FLAG% ^
    --clean ^
    main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo BUILD FAILED - check red errors above.
    pause
    exit /b 1
)
echo.
echo ==========================================
echo   SUCCESS
echo   File: dist\KarimStickerStudio.exe
echo ==========================================
pause
