@echo off
REM Build BubbleTrack into a single .exe for Windows
setlocal

echo ======================================
echo   Building BubbleTrack for Windows
echo ======================================
echo.

REM --- Ensure dependencies ---
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller -q
)

REM --- Clean previous build ---
if exist dist\BubbleTrack.exe del dist\BubbleTrack.exe

REM --- Build ---
echo Running PyInstaller...
pyinstaller build_onefile.spec --noconfirm --clean

echo.
if exist dist\BubbleTrack.exe (
    echo ======================================
    echo   Build successful!
    echo   Output: dist\BubbleTrack.exe
    echo ======================================
) else (
    echo ERROR: Build failed. Check output above.
    exit /b 1
)
