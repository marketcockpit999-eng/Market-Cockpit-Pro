@echo off
echo ========================================
echo Market Cockpit Pro - キャッシュクリア
echo ========================================

cd /d "%~dp0"

if exist ".market_data_cache.pkl" (
    del ".market_data_cache.pkl"
    echo ✅ キャッシュファイルを削除しました
) else (
    echo ⚠️ キャッシュファイルが見つかりません（既に削除済み？）
)

echo.
echo 次のステップ:
echo 1. Streamlitアプリを再起動してください
echo 2. 「強制更新」ボタンをクリックしてください
echo.
pause
