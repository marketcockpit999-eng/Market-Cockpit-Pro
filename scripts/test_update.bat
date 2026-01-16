@echo off
chcp 65001 >nul
REM ============================================================================
REM Quick test of the scheduled update script
REM ============================================================================

echo ============================================
echo Testing Scheduled Data Update Script
echo ============================================
echo.

cd /d "C:\Users\81802\.gemini\antigravity\scratch\market_monitor"

echo Running update_data.py with --verbose flag...
echo.
python scripts\update_data.py --verbose --force

echo.
echo ============================================
echo Test complete. Check output above for errors.
echo ============================================
pause
