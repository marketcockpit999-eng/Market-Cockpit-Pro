# -*- coding: utf-8 -*-
"""
i18n (多言語対応) テスト
================================================================================
日本語翻訳が消えていないか、英語と日本語のキーが一致しているかを確認

Usage:
    pytest tests/test_i18n.py -v
================================================================================
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_i18n_imports():
    """i18nモジュールがインポートできることを確認"""
    from utils.i18n import TRANSLATIONS, t, get_current_language
    assert TRANSLATIONS is not None
    assert callable(t)


def test_english_translations_exist():
    """英語翻訳が存在することを確認"""
    from utils.i18n import TRANSLATIONS
    
    assert 'en' in TRANSLATIONS, "英語翻訳セクションがありません"
    assert len(TRANSLATIONS['en']) > 50, f"英語キーが少なすぎます: {len(TRANSLATIONS['en'])}個"


def test_japanese_translations_exist():
    """日本語翻訳が存在することを確認（最重要）"""
    from utils.i18n import TRANSLATIONS
    
    assert 'ja' in TRANSLATIONS, "日本語翻訳セクションがありません"
    
    ja_count = len(TRANSLATIONS['ja'])
    assert ja_count > 50, f"⚠️ 日本語翻訳が少なすぎます: {ja_count}個（50個以上必要）"


def test_i18n_keys_match():
    """英語と日本語のキーが一致していることを確認"""
    from utils.i18n import TRANSLATIONS
    
    en_keys = set(TRANSLATIONS['en'].keys())
    ja_keys = set(TRANSLATIONS['ja'].keys())
    
    # 英語にあって日本語にないキー
    missing_in_ja = en_keys - ja_keys
    
    # 日本語にあって英語にないキー
    extra_in_ja = ja_keys - en_keys
    
    error_msg = []
    if missing_in_ja:
        error_msg.append(f"日本語翻訳がないキー ({len(missing_in_ja)}個): {list(missing_in_ja)[:10]}...")
    if extra_in_ja:
        error_msg.append(f"英語にないキー ({len(extra_in_ja)}個): {list(extra_in_ja)[:10]}...")
    
    assert en_keys == ja_keys, "\n".join(error_msg)


def test_t_function_returns_translated_text():
    """t()関数が翻訳テキストを返すことを確認"""
    from utils.i18n import t, TRANSLATIONS
    
    # 英語キーで取得
    result = t('app_title')
    assert result == 'Market Cockpit Pro', f"app_titleの翻訳が間違っています: {result}"


def test_no_empty_translations():
    """空の翻訳がないことを確認"""
    from utils.i18n import TRANSLATIONS
    
    empty_en = [k for k, v in TRANSLATIONS['en'].items() if not v or v.strip() == '']
    empty_ja = [k for k, v in TRANSLATIONS['ja'].items() if not v or v.strip() == '']
    
    assert len(empty_en) == 0, f"英語に空の翻訳があります: {empty_en}"
    assert len(empty_ja) == 0, f"日本語に空の翻訳があります: {empty_ja}"


if __name__ == "__main__":
    # 直接実行時のテスト
    print("=" * 60)
    print("[i18n] TEST")
    print("=" * 60)
    
    try:
        test_i18n_imports()
        print("[OK] test_i18n_imports")
    except AssertionError as e:
        print(f"[NG] test_i18n_imports: {e}")
    
    try:
        test_english_translations_exist()
        print("[OK] test_english_translations_exist")
    except AssertionError as e:
        print(f"[NG] test_english_translations_exist: {e}")
    
    try:
        test_japanese_translations_exist()
        print("[OK] test_japanese_translations_exist")
    except AssertionError as e:
        print(f"[NG] test_japanese_translations_exist: {e}")
    
    try:
        test_i18n_keys_match()
        print("[OK] test_i18n_keys_match")
    except AssertionError as e:
        print(f"[NG] test_i18n_keys_match: {e}")
    
    try:
        test_t_function_returns_translated_text()
        print("[OK] test_t_function_returns_translated_text")
    except AssertionError as e:
        print(f"[NG] test_t_function_returns_translated_text: {e}")
    
    try:
        test_no_empty_translations()
        print("[OK] test_no_empty_translations")
    except AssertionError as e:
        print(f"[NG] test_no_empty_translations: {e}")
    
    print("=" * 60)
