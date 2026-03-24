@echo off
REM Build BubbleTrack into a single .exe using a clean virtual environment
setlocal enabledelayedexpansion

set BUILD_ENV=.build_env

echo ======================================
echo   Building BubbleTrack for Windows
echo ======================================
echo.

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
exit /b 1

:found
for /f "tokens=*" %%V in ('%PYTHON% --version') do echo Using %PYTHON% (%%V)

REM --- Create clean build environment ---
if exist "%BUILD_ENV%\Scripts\python.exe" (
    echo Reusing build environment at %BUILD_ENV%
) else (
    echo Creating clean build environment...
    %PYTHON% -m venv %BUILD_ENV%
)

REM --- Install only required dependencies ---
echo Installing dependencies...
%BUILD_ENV%\Scripts\pip install --upgrade pip -q
%BUILD_ENV%\Scripts\pip install -e . -q
%BUILD_ENV%\Scripts\pip install pyinstaller -q

REM --- Clean previous build ---
if exist build\build_onefile rd /s /q build\build_onefile 2>nul
if exist dist\BubbleTrack.exe del dist\BubbleTrack.exe

REM --- Build ---
echo Running PyInstaller...
%BUILD_ENV%\Scripts\pyinstaller build_onefile.spec --noconfirm

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
