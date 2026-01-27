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
)
from utils.element_gap_checker import (
    ElementGapChecker,
    run_element_gap_check,
    classify_all_indicators,
    ELEMENT_PATTERNS,
)


def render_admin_page():
    """Render the admin dashboard page"""
    st.title("🔧 Admin Dashboard")
    st.caption("システム管理・診断ツール")
    
    # Get data from session state
    df = st.session_state.get('df')
    df_original = st.session_state.get('df_original')
    
    # Create tabs for different admin sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 データ鮮度",
        "🔍 構成要素チェック",
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
    # TAB 2: Element Gap Check (構成要素チェック) - NEW!
    # =========================================================================
    with tab2:
        render_element_gap_tab(df)
    
    # =========================================================================
    # TAB 3: Display Pattern Check (表示パターンチェック)
    # =========================================================================
    with tab3:
        render_display_pattern_tab()
    
    # =========================================================================
    # TAB 4: API Status (API状況)
    # =========================================================================
    with tab4:
        render_api_status_tab()
    
    # =========================================================================
    # TAB 5: System Info (システム情報)
    # =========================================================================
    with tab5:
        render_system_info_tab(df)


def render_element_gap_tab(df):
    """Render the element gap check tab (構成要素チェック)"""
    st.subheader("🔍 構成要素ギャップチェック")
    st.caption("各指標が『あるべき構成要素』を持っているか検証します")
    
    # Run checker
    checker = run_element_gap_check(df)
    summary = checker.get_summary()
    
    # Big score display
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        score_text = summary['score']
        ok_count = summary['ok']
        total = summary['total']
        
        # Color based on status
        if summary['fail'] == 0 and summary['warn'] == 0:
            st.success(f"✅ {score_text} 全指標OK!")
        elif summary['fail'] == 0:
            st.warning(f"⚠️ {score_text} ({summary['warn']}件の警告あり)")
        else:
            st.error(f"❌ {score_text} ({summary['fail']}件の必須欠落)")
    
    with col2:
        st.metric("OK", f"✅ {summary['ok']}")
    with col3:
        st.metric("問題あり", f"⚠️ {summary['warn'] + summary['fail']}")
    
    st.divider()
    
    # Pattern classification summary
    st.write("### パターン別サマリー")
    
    classification = classify_all_indicators()
    
    cols = st.columns(4)
    pattern_display = [
        ('A_daily_weekly', '日次/週次フル', '10要素'),
        ('B1_monthly_simple', '月次/四半期', '9要素'),
        ('B2_mom_yoy', 'MoM/YoY', '特殊'),
        ('API_external', 'API系', '別処理'),
    ]
    
    for i, (key, name, elem_count) in enumerate(pattern_display):
        with cols[i]:
            count = len(classification.get(key, []))
            pattern_stats = summary['by_pattern'].get(ELEMENT_PATTERNS.get(key, {}).get('name', key), {})
            ok = pattern_stats.get('ok', 0)
            st.metric(f"{name}", f"{ok}/{count}")
            st.caption(elem_count)
    
    st.divider()
    
    # Problem indicators detail
    problems = checker.get_problem_indicators()
    
    if problems:
        st.write("### ⚠️ 問題のある指標")
        
        for name, result in problems:
            status_icon = '❌' if result['status'] == 'FAIL' else '⚠️'
            
            with st.expander(f"{status_icon} {name} ({result['pattern']}) - {result['present']}/{result['expected']}要素", expanded=(result['status'] == 'FAIL')):
                col1, col2 = st.columns(2)
                
                with col1:
                    if result['missing_mandatory']:
                        st.error(f"**必須欠落:** {', '.join(result['missing_mandatory'])}")
                
                with col2:
                    if result['missing_optional']:
                        st.warning(f"**オプション欠落:** {', '.join(result['missing_optional'])}")
                
                # アクション提案
                if result['missing_mandatory']:
                    st.info("💡 **修正方法:**\n" + 
                           "\n".join([f"- {elem}: 対応が必要" for elem in result['missing_mandatory']]))
    else:
        st.success("🎉 全ての指標が期待される構成要素を持っています！")
    
    st.divider()
    
    # Full list (collapsed)
    with st.expander("📋 全指標リスト", expanded=False):
        rows = []
        for name, result in checker.results.items():
            status_emoji = {'OK': '✅', 'WARN': '⚠️', 'FAIL': '❌', 'UNKNOWN': '❓'}.get(result['status'], '?')
            rows.append({
                'Status': status_emoji,
                'Indicator': name,
                'Pattern': result['pattern'],
                'Elements': f"{result['present']}/{result['expected']}",
                'Missing': ', '.join(result.get('missing_mandatory', []) + result.get('missing_optional', []))[:50] or '-',
            })
        
        df_table = pd.DataFrame(rows)
        df_table = df_table.sort_values(['Status', 'Indicator'], ascending=[True, True])
        
        st.dataframe(
            df_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn("", width="small"),
                "Indicator": st.column_config.TextColumn("指標名", width="medium"),
                "Pattern": st.column_config.TextColumn("パターン", width="small"),
                "Elements": st.column_config.TextColumn("要素", width="small"),
                "Missing": st.column_config.TextColumn("欠落", width="large"),
            }
        )


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
    st.caption("構成要素の検証結果（DisplayChecker）")
    
    try:
        # verify_display_patterns returns a DisplayChecker object
        checker = verify_display_patterns()
        
        if checker is None or not hasattr(checker, 'results'):
            st.info("パターン検証結果がありません")
            return
        
        # Get summary from checker
        results = checker.results  # Dict of CheckResult objects
        
        # Summary metrics
        total = len(results)
        ok_count = sum(1 for r in results.values() if r.is_ok)
        fail_count = total - ok_count
        
        col1, col2, col3 = st.columns(3)
        col1.metric("総指標数", total)
        col2.metric("✅ OK", ok_count)
        col3.metric("⚠️ 要確認", fail_count)
        
        st.divider()
        
        # Group by group type
        by_group = {}
        for name, result in results.items():
            group = result.group
            if group not in by_group:
                by_group[group] = {'ok': [], 'fail': []}
            if result.is_ok:
                by_group[group]['ok'].append(name)
            else:
                by_group[group]['fail'].append((name, result))
        
        # Display by group
        group_names = {
            'daily_weekly': '📈 日次/週次フル (10要素)',
            'monthly_quarterly': '📅 月次/四半期 (9要素)',
            'mom_yoy': '📊 MoM/YoY (特殊)',
            'api': '🔌 API系 (別処理)',
        }
        
        for group_key, display_name in group_names.items():
            group_data = by_group.get(group_key, {'ok': [], 'fail': []})
            ok_list = group_data['ok']
            fail_list = group_data['fail']
            total_in_group = len(ok_list) + len(fail_list)
            
            if total_in_group == 0:
                continue
            
            with st.expander(f"{display_name} ({len(ok_list)}/{total_in_group} OK)", expanded=(len(fail_list) > 0)):
                if fail_list:
                    st.write("**⚠️ 問題のある指標:**")
                    for name, result in fail_list:
                        failed_elements = ', '.join(result.failed)
                        st.warning(f"`{name}`: 欠落要素 = {failed_elements}")
                
                if ok_list:
                    st.write("**✅ OK:**")
                    st.caption(", ".join(sorted(ok_list)))
        
        # Show failed indicators detail
        all_failed = [(name, r) for name, r in results.items() if not r.is_ok]
        if all_failed:
            st.divider()
            st.write("### ⚠️ 修正が必要な指標")
            for name, result in sorted(all_failed, key=lambda x: x[0]):
                with st.expander(f"⚠️ {name} ({result.score_text})", expanded=False):
                    st.write(f"**グループ:** {result.group}")
                    st.write(f"**欠落要素:** {', '.join(result.failed)}")
                    for elem in result.failed:
                        detail = result.details.get(elem, '')
                        st.caption(f"  - {elem}: {detail}")
    
    except Exception as e:
        st.error(f"パターン検証エラー: {e}")
        import traceback
        st.code(traceback.format_exc())
        st.info("構成要素チェックタブをご利用ください")

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
