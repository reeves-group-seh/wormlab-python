@echo off

@REM move to script directory
cd /d "%~dp0"

@REM pull updates
git checkout stable && git pull --ff-only || (
    echo.
    echo run: failed to pull updates
    pause
    exit /b 1
)

@REM sync deps
uv sync || (
    echo.
    echo run: failed to install dependencies
    pause
    exit /b 1
)

@REM run
uv run shooter
