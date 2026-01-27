# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Pre-commit Hook Setup
================================================================================
pre-commit hookをインストールするセットアップスクリプト

使い方:
    python scripts/setup_hooks.py

何をするか:
    1. .git/hooks/pre-commit にhookをコピー
    2. 実行権限を設定

================================================================================
"""

import os
import shutil
import stat
import sys

# プロジェクトルート
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT_HOOKS_DIR = os.path.join(PROJECT_ROOT, '.git', 'hooks')
HOOK_SCRIPT = os.path.join(PROJECT_ROOT, 'scripts', 'pre-commit-hook.sh')
TARGET_HOOK = os.path.join(GIT_HOOKS_DIR, 'pre-commit')


def setup_pre_commit_hook():
    """pre-commit hookをセットアップ"""
    
    print("=" * 60)
    print("Market Cockpit Pro - Pre-commit Hook Setup")
    print("=" * 60)
    print()
    
    # .git ディレクトリの確認
    if not os.path.exists(os.path.join(PROJECT_ROOT, '.git')):
        print("❌ Error: .git directory not found!")
        print("   This script must be run from a Git repository.")
        return 1
    
    # hooks ディレクトリの作成
    if not os.path.exists(GIT_HOOKS_DIR):
        os.makedirs(GIT_HOOKS_DIR)
        print(f"📁 Created hooks directory: {GIT_HOOKS_DIR}")
    
    # ソーススクリプトの確認
    if not os.path.exists(HOOK_SCRIPT):
        print(f"❌ Error: Hook script not found: {HOOK_SCRIPT}")
        return 1
    
    # 既存のhookをバックアップ
    if os.path.exists(TARGET_HOOK):
        backup_path = TARGET_HOOK + '.backup'
        shutil.copy2(TARGET_HOOK, backup_path)
        print(f"📦 Backed up existing hook to: {backup_path}")
    
    # hookをコピー
    shutil.copy2(HOOK_SCRIPT, TARGET_HOOK)
    print(f"✅ Installed pre-commit hook: {TARGET_HOOK}")
    
    # 実行権限を設定 (Unix系OS用)
    try:
        st = os.stat(TARGET_HOOK)
        os.chmod(TARGET_HOOK, st.st_mode | stat.S_IEXEC)
        print("✅ Set executable permission")
    except Exception as e:
        print(f"⚠️  Warning: Could not set executable permission: {e}")
        print("   On Windows, this is usually not needed.")
    
    print()
    print("=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Pre-commit hookがインストールされました。")
    print()
    print("これで、git commit時に自動的に検証が実行されます。")
    print("検証に失敗すると、commitがブロックされます。")
    print()
    print("手動で検証を実行するには:")
    print("  python scripts/verify_baseline.py")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(setup_pre_commit_hook())
