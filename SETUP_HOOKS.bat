@echo off
REM ================================================================================
REM Market Cockpit Pro - Setup Pre-commit Hook
REM pre-commit hookをインストールするバッチファイル
REM ================================================================================

echo.
echo ================================================
echo Market Cockpit Pro - Pre-commit Hook Setup
echo ================================================
echo.

cd /d "%~dp0"
python scripts/setup_hooks.py

echo.
pause
