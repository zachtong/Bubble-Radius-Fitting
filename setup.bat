@echo off
REM BubbleTrack setup script for Windows
setlocal enabledelayedexpansion

set VENV_DIR=.venv

REM --- Find Python 3.10+ ---
set PYTHON=
for %%P in (python py) do (
    where %%P >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%V in ('%%P -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2^>nul') do (
            for /f "tokens=1,2 delims=." %%A in ("%%V") do (
                if %%A geq 3 if %%B geq 10 (
                    set PYTHON=%%P
                    goto :found
                )
            )
        )
    )
)

echo ERROR: Python 3.10+ is required but not found.
echo Download from https://www.python.org/downloads/
exit /b 1

:found
for /f "tokens=*" %%V in ('%PYTHON% --version') do echo Using %PYTHON% (%%V)

REM --- Create virtual environment ---
if exist "%VENV_DIR%\Scripts\python.exe" (
    echo Virtual environment already exists, updating...
) else (
    echo Creating virtual environment...
    %PYTHON% -m venv %VENV_DIR%
)

REM --- Install into venv ---
echo Installing BubbleTrack...
%VENV_DIR%\Scripts\pip install --upgrade pip -q
%VENV_DIR%\Scripts\pip install -e . -q

REM --- Create launcher ---
(
    echo @echo off
    echo "%%~dp0.venv\Scripts\bubbletrack.exe"
)> BubbleTrack.bat

echo.
echo ======================================
echo   BubbleTrack installed successfully!
echo ======================================
echo.
echo Double-click BubbleTrack.bat to launch.
