@echo off
echo Stopping old Streamlit...
taskkill /f /im streamlit.exe 2>nul
taskkill /f /im python.exe 2>nul
timeout /t 2 >nul
echo Starting Market Cockpit Pro...
cd /d "C:\Users\81802\.gemini\antigravity\scratch\market_monitor"
start streamlit run market_app_nav.py
echo Done! Browser will open automatically.
