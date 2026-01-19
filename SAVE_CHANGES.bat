@echo off
chcp 65001 > nul
echo.
echo ========================================
echo   Market Cockpit Pro - 変更を保存
echo ========================================
echo.

cd /d "%~dp0"

echo 変更されたファイル:
git status --short
echo.

set /p msg="コミットメッセージ (何も入力せずEnterで「update」): "
if "%msg%"=="" set msg=update

git add -A
git commit -m "%msg%"

echo.
echo ✅ 保存完了！
echo.
pause
