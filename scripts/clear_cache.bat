@echo off
chcp 65001 >nul
echo ========================================
echo Market Cockpit Pro - Full Cache Clear
echo ========================================
echo.

cd /d "C:\Users\81802\.gemini\antigravity\scratch\market_monitor"

echo [1/4] Deleting disk cache...
if exist ".market_data_cache.pkl" (
    del /F /Q ".market_data_cache.pkl"
    echo       Deleted: .market_data_cache.pkl
) else (
    echo       Not found: .market_data_cache.pkl
)

echo.
echo [2/4] Deleting Streamlit cache...
if exist "%USERPROFILE%\.streamlit\cache" (
    rd /S /Q "%USERPROFILE%\.streamlit\cache"
    echo       Deleted: Streamlit cache folder
) else (
    echo       Not found: Streamlit cache
)

echo.
echo [3/4] Deleting Python __pycache__...
if exist "utils\__pycache__" (
    rd /S /Q "utils\__pycache__"
    echo       Deleted: utils\__pycache__
) else (
    echo       Not found: utils\__pycache__
)
if exist "pages\__pycache__" (
    rd /S /Q "pages\__pycache__"
    echo       Deleted: pages\__pycache__
) else (
    echo       Not found: pages\__pycache__
)
if exist "__pycache__" (
    rd /S /Q "__pycache__"
    echo       Deleted: __pycache__
) else (
    echo       Not found: __pycache__
)

echo.
echo [4/4] Running health check...
python scripts\health_check.py

echo.
echo ========================================
echo Cache cleared! Now restart the app:
echo   python -m streamlit run market_app_nav.py
echo ========================================
pause
