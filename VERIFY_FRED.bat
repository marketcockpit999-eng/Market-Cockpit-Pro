@echo off
echo ========================================
echo FRED Data Verification
echo ========================================
echo.
echo Running FRED status check...
cd /d %~dp0..
python scripts\check_fred_status.py
echo.
echo ----------------------------------------
echo.
echo Running FRED data verification...
python scripts\verify_fred_data.py
echo.
echo ========================================
echo Verification complete
echo ========================================
pause
