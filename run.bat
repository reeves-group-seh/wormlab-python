@echo off

@REM move to script directory
cd /d "%~dp0"

@REM sync deps
uv sync || (
    echo.
    echo run: failed to install dependencies
    pause
    exit /b 1
)

@REM run
uv run stage-ui
