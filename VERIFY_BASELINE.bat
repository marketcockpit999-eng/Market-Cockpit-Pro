@echo off
REM ================================================================================
REM Market Cockpit Pro - Run Baseline Verification
REM 指標のベースライン検証を手動で実行するためのバッチファイル
REM ================================================================================

echo.
echo ================================================
echo Market Cockpit Pro - Baseline Verification
echo ================================================
echo.

cd /d "%~dp0.."
python scripts/verify_baseline.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo ✓ Verification passed!
) else (
    echo ✗ Verification failed!
    echo   Please fix the issues above.
)
echo.
pause
