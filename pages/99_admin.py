# -*- coding: utf-8 -*-
"""
Market Cockpit Pro - Admin Dashboard
================================================================================
管理者用ダッシュボード: データ鮮度、表示パターン、API状況を一覧表示

機能:
  1. データ鮮度一覧 (101項目)
  2. 表示パターンチェック結果
  3. API接続状況
  4. キャッシュ管理
  5. システム情報
================================================================================
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime

from utils import (
    t,
    get_data_freshness_status,
    get_api_status,
    INDICATORS,
    get_all_indicator_names,
)
from utils.display_checker import (
    verify_display_patterns,
    DisplayChecker,
    run_static_check,
)


def render_admin_page():
    """Render the admin dashboard page"""
    st.title("🔧 Admin Dashboard")
    st.caption("システム管理・診断ツール")
    
    # Get data from session state
    df = st.session_state.get('df')
    df_original = st.session_state.get('df_original')
    
    # Create tabs for different admin sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 データ鮮度",
        "✅ 表示パターン",
        "🔌 API状況",
        "⚙️ システム情報",
    ])
    
    # =========================================================================
    # TAB 1: Data Freshness (データ鮮度)
    # =========================================================================
    with tab1:
        render_data_freshness_tab(df)
    
    # =========================================================================
    # TAB 2: Display Pattern Check (表示パターンチェック)
    # =========================================================================
    with tab2:
        render_display_pattern_tab()
    
    # =========================================================================
    # TAB 3: API Status (API状況)
    # =========================================================================
    with tab3:
        render_api_status_tab()
    
    # =========================================================================
    # TAB 4: System Info (システム情報)
    # =========================================================================
    with tab4:
        render_system_info_tab(df)


def render_data_freshness_tab(df):
    """Render the data freshness tab"""
    st.subheader("📊 データ鮮度一覧")
    
    if df is None or not hasattr(df, 'attrs'):
        st.warning("データが読み込まれていません。メインページで読み込んでください。")
        return
    
    # Get freshness status
    last_valid_dates = df.attrs.get('last_valid_dates', {})
    release_dates = df.attrs.get('fred_release_dates', {})
    api_status = get_api_status()
    
    freshness = get_data_freshness_status(last_valid_dates, release_dates, api_status)
    
    # Summary metrics
    summary = freshness['summary']
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total", summary['total'])
    col2.metric("🟢 Fresh", summary['fresh_count'])
    col3.metric("🟡 Stale", summary['stale_count'])
    col4.metric("🔴 Critical", summary['critical_count'])
    col5.metric("⚪ Missing", summary['missing_count'])
    
    st.metric("Health Score", f"{summary['health_score']}%")
    
    st.divider()
    
    # Filter options
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        status_filter = st.multiselect(
            "ステータスでフィルタ",
            options=["fresh", "stale", "critical", "missing"],
            default=["stale", "critical", "missing"],
            format_func=lambda x: {"fresh": "🟢 Fresh", "stale": "🟡 Stale", "critical": "🔴 Critical", "missing": "⚪ Missing"}[x]
        )
    with col_filter2:
        show_api_only = st.checkbox("API指標のみ表示", value=False)
    
    # Build detail table
    rows = []
    for indicator, detail in freshness['details'].items():
        if detail['status'] not in status_filter:
            continue
        if show_api_only and not detail.get('is_api', False):
            continue
        
        status_emoji = {
            'fresh': '🟢',
            'stale': '🟡',
            'critical': '🔴',
            'missing': '⚪'
        }.get(detail['status'], '❓')
        
        rows.append({
            'Status': status_emoji,
            'Indicator': indicator,
            'Last Date': detail.get('last_date') or 'N/A',
            'Days Old': detail.get('days_old') if detail.get('days_old') is not None else '-',
            'Category': detail.get('category', 'Unknown'),
            'API': '✓' if detail.get('is_api') else '',
            'Expected Max': detail.get('expected_max') or '-',
        })
    
    if rows:
        df_table = pd.DataFrame(rows)
        st.dataframe(
            df_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn("", width="small"),
                "Indicator": st.column_config.TextColumn("指標名", width="medium"),
                "Last Date": st.column_config.TextColumn("最終日付", width="small"),
                "Days Old": st.column_config.NumberColumn("経過日数", width="small"),
                "Category": st.column_config.TextColumn("カテゴリ", width="small"),
                "API": st.column_config.TextColumn("API", width="small"),
                "Expected Max": st.column_config.NumberColumn("許容日数", width="small"),
            }
        )
        st.caption(f"表示中: {len(rows)} 件")
    else:
        st.info("該当する指標がありません")


def render_display_pattern_tab():
    """Render the display pattern check tab"""
    st.subheader("✅ 表示パターンチェック")
    
    # Run verification
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    with st.spinner("パターン検証中..."):
        results = verify_display_patterns(app_root)
    
    # Summary
    total_found = (
        len(results['pattern_standard']) + 
        len(results['pattern_detailed']) + 
        len(results['pattern_manual']) + 
        len(results['pattern_special'])
    )
    error_count = len(results['errors'])
    mismatch_count = len(results.get('pattern_mismatches', []))
    warning_count = len([w for w in results.get('element_warnings', []) if w['severity'] == 'WARN'])
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("検出済み指標", total_found)
    col2.metric("Standard (Sparkline)", len(results['pattern_standard']))
    col3.metric("Detailed (Macro Card)", len(results['pattern_detailed']))
    col4.metric("Manual / Special", len(results['pattern_manual']) + len(results['pattern_special']))
    
    # Status indicator
    if error_count == 0 and mismatch_count == 0:
        st.success("✅ All patterns match their expected display functions!")
    else:
        st.error(f"❌ {error_count + mismatch_count} issue(s) found")
    
    st.divider()
    
    # Pattern breakdown
    with st.expander("📋 Standard Pattern (show_metric_with_sparkline)", expanded=False):
        if results['pattern_standard']:
            by_file = {}
            for item in results['pattern_standard']:
                file = item['file']
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append(item['key'])
            
            for file in sorted(by_file.keys()):
                st.write(f"**{file}** ({len(by_file[file])}件)")
                st.caption(", ".join(sorted(by_file[file])))
    
    with st.expander("📊 Detailed Pattern (display_macro_card)", expanded=False):
        if results['pattern_detailed']:
            for item in results['pattern_detailed']:
                st.write(f"- `{item['key']}` → {item['file']}")
    
    with st.expander("🔧 Manual / Custom Pattern", expanded=False):
        if results['pattern_manual']:
            for item in results['pattern_manual']:
                st.write(f"- `{item['key']}` → {item['file']} ({item['type']})")
    
    with st.expander("🔌 Special / API Pattern", expanded=False):
        if results['pattern_special']:
            for item in results['pattern_special']:
                st.write(f"- `{item['key']}`: {item['reason']}")
    
    # Errors and mismatches
    if results['errors']:
        with st.expander(f"❌ Errors ({len(results['errors'])})", expanded=True):
            for error in results['errors']:
                st.error(error)
    
    if results.get('pattern_mismatches'):
        with st.expander(f"⚠️ Pattern Mismatches ({len(results['pattern_mismatches'])})", expanded=True):
            for item in results['pattern_mismatches']:
                st.warning(f"`{item['key']}`: Expected `{item['expected']}` but found `{item['actual']}` in {item['file']}")
    
    # Element warnings (Phase 3.5)
    element_warnings = results.get('element_warnings', [])
    warn_items = [w for w in element_warnings if w['severity'] == 'WARN']
    if warn_items:
        with st.expander(f"⚠️ Element Warnings ({len(warn_items)})", expanded=False):
            for item in warn_items:
                st.warning(f"`{item['key']}` ({item['file']}): {item['message']}")


def render_api_status_tab():
    """Render the API status tab"""
    st.subheader("🔌 API接続状況")
    
    api_status = get_api_status()
    
    if not api_status:
        st.info("API状況データがありません。アプリ起動時に自動取得されます。")
        return
    
    # Summary
    total = len(api_status)
    success_count = sum(1 for v in api_status.values() if v.get('success'))
    fail_count = total - success_count
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total APIs", total)
    col2.metric("✅ Success", success_count)
    col3.metric("❌ Failed", fail_count)
    
    st.divider()
    
    # Detail table
    rows = []
    for name, status in api_status.items():
        rows.append({
            'Status': '✅' if status.get('success') else '❌',
            'API Name': name,
            'Last Fetch': status.get('last_fetch', 'N/A'),
            'Error': status.get('error', '') if not status.get('success') else '',
        })
    
    df_table = pd.DataFrame(rows)
    st.dataframe(
        df_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("", width="small"),
            "API Name": st.column_config.TextColumn("API名", width="medium"),
            "Last Fetch": st.column_config.TextColumn("最終取得日", width="small"),
            "Error": st.column_config.TextColumn("エラー", width="large"),
        }
    )


def render_system_info_tab(df):
    """Render the system info tab"""
    st.subheader("⚙️ システム情報")
    
    # Cache management
    st.write("### キャッシュ管理")
    
    cache_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '.market_data_cache.pkl'
    )
    
    if os.path.exists(cache_file):
        cache_stat = os.stat(cache_file)
        cache_size = cache_stat.st_size / 1024 / 1024  # MB
        cache_mtime = datetime.fromtimestamp(cache_stat.st_mtime)
        
        col1, col2 = st.columns(2)
        col1.metric("キャッシュサイズ", f"{cache_size:.2f} MB")
        col2.metric("最終更新", cache_mtime.strftime('%Y-%m-%d %H:%M:%S'))
        
        if st.button("🗑️ キャッシュを削除", type="secondary"):
            try:
                os.remove(cache_file)
                st.success("キャッシュを削除しました。ページを再読み込みしてください。")
                st.session_state['force_refresh'] = True
            except Exception as e:
                st.error(f"削除エラー: {e}")
    else:
        st.info("キャッシュファイルは存在しません")
    
    st.divider()
    
    # Indicator Registry Stats
    st.write("### 指標レジストリ統計")
    
    total_indicators = len(INDICATORS)
    
    # Count by source
    by_source = {}
    for name, config in INDICATORS.items():
        source = config.get('source', 'UNKNOWN')
        by_source[source] = by_source.get(source, 0) + 1
    
    # Count by pattern
    by_pattern = {}
    for name, config in INDICATORS.items():
        pattern = config.get('display_pattern', 'standard')
        by_pattern[pattern] = by_pattern.get(pattern, 0) + 1
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**ソース別**")
        for source, count in sorted(by_source.items()):
            st.write(f"- {source}: {count}")
    
    with col2:
        st.write("**表示パターン別**")
        for pattern, count in sorted(by_pattern.items()):
            st.write(f"- {pattern}: {count}")
    
    st.metric("総指標数", total_indicators)
    
    st.divider()
    
    # DataFrame Info
    st.write("### DataFrame情報")
    
    if df is not None:
        col1, col2, col3 = st.columns(3)
        col1.metric("行数", len(df))
        col2.metric("列数", len(df.columns))
        col3.metric("メモリ使用量", f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        st.write("**日付範囲:**")
        st.write(f"- 開始: {df.index.min()}")
        st.write(f"- 終了: {df.index.max()}")
    else:
        st.info("DataFrameが読み込まれていません")
    
    st.divider()
    
    # Version Info
    st.write("### バージョン情報")
    st.write("- **App Version:** 2.2.0 (i18n Edition)")
    st.write(f"- **Python:** {__import__('sys').version.split()[0]}")
    st.write(f"- **Streamlit:** {st.__version__}")
    st.write(f"- **Pandas:** {pd.__version__}")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
render_admin_page()
