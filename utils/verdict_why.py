# -*- coding: utf-8 -*-
"""
MARKET VERDICT - WHY Section Generator (Phase 4)
================================================================================
"Why This Verdict?" レポート生成ロジック

設計哲学（4人の巨人）:
- Ray Dalio: サイクルの位置を知れ
- Howard Marks: 振り子の極端を避けよ
- Stanley Druckenmiller: 流動性が全てを動かす
- Michael Howell: Net Liq = Fed Assets - TGA - ON_RRP

Usage:
    from utils.verdict_why import render_why_section
    render_why_section(verdict)
================================================================================
"""

import streamlit as st
from utils.i18n import t, get_current_language


def get_lang():
    return get_current_language()


# =============================================================================
# 投資家の名言・視点（定数）
# =============================================================================
QUOTES = {
    'druckenmiller': {
        'bullish_ja': "「流動性が潤沢な時、資産価格は上昇する」— Druckenmiller",
        'bullish_en': '"When liquidity is abundant, asset prices rise." — Druckenmiller',
        'neutral_ja': "「流動性の方向を見極めろ」— Druckenmiller",
        'neutral_en': '"Watch the direction of liquidity." — Druckenmiller',
        'bearish_ja': "「流動性が引き上げられる時、慎重になれ」— Druckenmiller",
        'bearish_en': '"Be cautious when liquidity is being withdrawn." — Druckenmiller',
    },
    'howell': {
        'formula_ja': "Net Liquidity = Fed資産 − TGA − ON_RRP（Howell公式）",
        'formula_en': "Net Liquidity = Fed Assets − TGA − ON_RRP (Howell Formula)",
        'insight_ja': "「グローバル流動性が資産クラスを支配する」— Michael Howell",
        'insight_en': '"Global liquidity dominates asset classes." — Michael Howell',
    },
    'dalio': {
        'expansion_ja': "「拡大期は株式を買え」— Dalio's All Weather",
        'expansion_en': '"Buy equities in expansion." — Dalio\'s All Weather',
        'slowdown_ja': "「減速期は質の高い資産へ移行せよ」— Dalio",
        'slowdown_en': '"Shift to quality assets in slowdown." — Dalio',
        'recession_ja': "「冬に備えよ。債券とゴールドを」— Dalio",
        'recession_en': '"Prepare for winter. Bonds and Gold." — Dalio',
    },
    'marks': {
        'greed_ja': "「皆が強気の時こそ、我々は慎重になるべき」— Howard Marks",
        'greed_en': '"When everyone is greedy, we should be cautious." — Howard Marks',
        'fear_ja': "「振り子が恐怖に振れた極端な時こそ好機」— Howard Marks",
        'fear_en': '"The best opportunities arise when the pendulum swings to fear." — Howard Marks',
        'neutral_ja': "「準備せよ、予測するな」— Howard Marks",
        'neutral_en': '"You can\'t predict. You can prepare." — Howard Marks',
    }
}


# =============================================================================
# 各柱の解説関数
# =============================================================================

def explain_liquidity(pillar: dict) -> str:
    """
    流動性スコアの解説
    Druckenmiller: 流動性が全てを動かす
    Howell: Net Liq = Fed - TGA - RRP
    """
    score = pillar.get('score', 50)
    details = pillar.get('details', {})
    lang = get_lang()
    
    # データ取得
    net_liq = details.get('net_liquidity', {})
    net_liq_val = net_liq.get('value', 0) / 1000 if net_liq.get('value') else 0  # T
    fed_assets = details.get('fed_assets', {})
    fed_val = fed_assets.get('value', 0) / 1000 if fed_assets.get('value') else 0  # T
    tga = details.get('tga', {})
    tga_val = tga.get('value', 0) if tga.get('value') else 0  # B
    on_rrp = details.get('on_rrp', {})
    rrp_val = on_rrp.get('value', 0) if on_rrp.get('value') else 0  # B
    
    # Howell公式の表示
    howell_formula = QUOTES['howell'][f'formula_{lang}']
    
    if lang == 'ja':
        if score >= 65:
            title = "💧 流動性は「追い風」"
            status = f"Net Liquidity: **${net_liq_val:.2f}T**（Fed ${fed_val:.2f}T − TGA ${tga_val:.0f}B − RRP ${rrp_val:.0f}B）"
            quote = QUOTES['druckenmiller']['bullish_ja']
            insight = "リスク資産にとって良好な環境。"
            if tga_val > 600:
                warning = f"⚠️ TGAが${tga_val:.0f}Bと高水準。国債発行で流動性吸収の可能性あり。"
            else:
                warning = ""
        elif score >= 45:
            title = "💧 流動性は「中立」"
            status = f"Net Liquidity: **${net_liq_val:.2f}T**"
            quote = QUOTES['druckenmiller']['neutral_ja']
            insight = "特段の追い風も向かい風もない状況。"
            warning = "QT（量的引締め）のペースと銀行準備金に注目。"
        else:
            title = "💧 流動性に「黄信号」"
            status = f"Net Liquidity: **${net_liq_val:.2f}T** と縮小傾向"
            quote = QUOTES['druckenmiller']['bearish_ja']
            insight = QUOTES['howell']['insight_ja']
            warning = "リザーブ不足による市場の動揺に警戒。"
    else:
        if score >= 65:
            title = "💧 Liquidity: Tailwind"
            status = f"Net Liquidity: **${net_liq_val:.2f}T** (Fed ${fed_val:.2f}T − TGA ${tga_val:.0f}B − RRP ${rrp_val:.0f}B)"
            quote = QUOTES['druckenmiller']['bullish_en']
            insight = "Favorable environment for risk assets."
            if tga_val > 600:
                warning = f"⚠️ TGA at ${tga_val:.0f}B is elevated. Treasury issuance may absorb liquidity."
            else:
                warning = ""
        elif score >= 45:
            title = "💧 Liquidity: Neutral"
            status = f"Net Liquidity: **${net_liq_val:.2f}T**"
            quote = QUOTES['druckenmiller']['neutral_en']
            insight = "Neither tailwind nor headwind."
            warning = "Watch QT pace and bank reserves."
        else:
            title = "💧 Liquidity: Warning"
            status = f"Net Liquidity: **${net_liq_val:.2f}T** and shrinking"
            quote = QUOTES['druckenmiller']['bearish_en']
            insight = QUOTES['howell']['insight_en']
            warning = "Watch for market stress from reserve scarcity."

    # 組み立て
    parts = [f"**{title}**", "", f"📐 {howell_formula}", "", status, "", f"*{quote}*", "", insight]
    if warning:
        parts.append("")
        parts.append(warning)
    
    return "\n".join(parts)


def explain_cycle(pillar: dict) -> str:
    """
    サイクルスコアの解説
    Ray Dalio: サイクルの位置を知れ
    """
    score = pillar.get('score', 50)
    details = pillar.get('details', {})
    lang = get_lang()
    
    yield_curve = details.get('yield_curve', {}).get('value', 0)
    unrate = details.get('unemployment', {}).get('value', 0)
    
    if lang == 'ja':
        if score >= 70:
            title = "🔄 サイクルは「拡大期」"
            desc = "経済活動は活発、リセッション懸念は後退。"
            phase = "Dalio流「サマー」〜「初秋」: 株価上昇、金利上昇の局面。"
            quote = QUOTES['dalio']['expansion_ja']
            action = "**推奨**: シクリカル、グロース株に優位性。"
        elif score >= 40:
            title = "🔄 サイクルは「減速・成熟期」"
            curve_status = f"イールドカーブ: {yield_curve:+.2f}%" if yield_curve else ""
            unemp_status = f"失業率: {unrate:.1f}%" if unrate else ""
            desc = f"{curve_status}、{unemp_status}"
            phase = "サイクルの転換点に近い兆候。"
            quote = QUOTES['dalio']['slowdown_ja']
            action = "**推奨**: クオリティ株への選別が必要。"
        else:
            title = "🔄 サイクルは「後退懸念」"
            desc = "先行指標が悪化、リセッションリスク上昇。"
            phase = "Dalio流「冬」の準備期。"
            quote = QUOTES['dalio']['recession_ja']
            action = "**推奨**: ディフェンシブ、債券、現金比率を高める。"
    else:
        if score >= 70:
            title = "🔄 Cycle: Expansion"
            desc = "Economic activity robust, recession fears receding."
            phase = "Dalio's 'Summer' to 'Early Fall': Rising stocks, rising rates."
            quote = QUOTES['dalio']['expansion_en']
            action = "**Favors**: Cyclicals and Growth stocks."
        elif score >= 40:
            title = "🔄 Cycle: Slowdown/Mature"
            curve_status = f"Yield Curve: {yield_curve:+.2f}%" if yield_curve else ""
            unemp_status = f"Unemployment: {unrate:.1f}%" if unrate else ""
            desc = f"{curve_status}, {unemp_status}"
            phase = "Signs of cycle turning point."
            quote = QUOTES['dalio']['slowdown_en']
            action = "**Favors**: Quality stock selection."
        else:
            title = "🔄 Cycle: Recession Risk"
            desc = "Leading indicators deteriorating, recession risk rising."
            phase = "Dalio's 'Winter' preparation phase."
            quote = QUOTES['dalio']['recession_en']
            action = "**Favors**: Defensives, Bonds, Cash."

    return f"**{title}**\n\n{desc}\n\n{phase}\n\n*{quote}*\n\n{action}"


def explain_technical(pillar: dict) -> str:
    """
    テクニカルスコアの解説
    トレンドフォロー視点
    """
    score = pillar.get('score', 50)
    details = pillar.get('details', {})
    lang = get_lang()
    
    ma_dev = details.get('ma_deviation', {}).get('deviation_pct', 0)
    rsi = details.get('rsi', {}).get('value', 50)
    pos_52w = details.get('position_52w', {}).get('position_pct', 50)
    
    if lang == 'ja':
        if score >= 70:
            title = "📈 トレンドは「強力な上昇」"
            desc = f"200日MA乖離: **{ma_dev:+.1f}%** / RSI: **{rsi:.0f}** / 52週位置: **{pos_52w:.0f}%**"
            insight = "「トレンドは友」の状態。押し目買いが有効な局面。"
            if ma_dev > 15:
                warning = "⚠️ 短期的には過熱感あり。利益確定も検討。"
            else:
                warning = ""
        elif score >= 40:
            title = "📈 トレンドは「中立〜レンジ」"
            desc = f"200日MA乖離: **{ma_dev:+.1f}%** / RSI: **{rsi:.0f}**"
            insight = "方向感が定まるのを待つ局面。"
            warning = ""
        else:
            title = "📈 トレンドは「下降」"
            desc = f"主要な移動平均線を下回って推移（{ma_dev:+.1f}%）"
            insight = "「落ちてくるナイフ」に注意。底打ち確認まで待機推奨。"
            warning = ""
    else:
        if score >= 70:
            title = "📈 Technical: Strong Uptrend"
            desc = f"200-day MA Deviation: **{ma_dev:+.1f}%** / RSI: **{rsi:.0f}** / 52w Position: **{pos_52w:.0f}%**"
            insight = "'Trend is your friend.' Buying dips is effective."
            if ma_dev > 15:
                warning = "⚠️ Short-term overheating. Consider taking some profit."
            else:
                warning = ""
        elif score >= 40:
            title = "📈 Technical: Neutral/Range"
            desc = f"200-day MA Deviation: **{ma_dev:+.1f}%** / RSI: **{rsi:.0f}**"
            insight = "Awaiting a clear directional break."
            warning = ""
        else:
            title = "📈 Technical: Downtrend"
            desc = f"Trading below key moving averages ({ma_dev:+.1f}%)"
            insight = "'Falling knife' risk. Wait for confirmed bottom."
            warning = ""

    parts = [f"**{title}**", "", desc, "", insight]
    if warning:
        parts.append("")
        parts.append(warning)
    return "\n".join(parts)


def explain_sentiment(pillar: dict) -> str:
    """
    センチメントスコアの解説
    Howard Marks: 振り子の極端を避けよ
    
    重要: 高スコア = 楽観/Greed（過熱）、低スコア = 恐怖/Fear（買い場）
    """
    score = pillar.get('score', 50)
    details = pillar.get('details', {})
    lang = get_lang()
    
    vix = details.get('vix', {}).get('value', 0)
    aaii = details.get('aaii_spread', {}).get('value')
    aaii_str = f"{aaii:+.0f}%" if aaii is not None else "N/A"
    
    # 振り子のメタファー
    if lang == 'ja':
        if score >= 75:
            # 高スコア = 楽観 = Marks流では「警戒」
            title = "📊 センチメント「過熱警戒」"
            pendulum = "🎯 振り子は**楽観（Greed）側**に大きく振れている"
            desc = f"VIX: **{vix:.1f}**（低水準）/ AAII Bull-Bear: **{aaii_str}**"
            quote = QUOTES['marks']['greed_ja']
            insight = "「皆が買っている時」に新規リスクを積むのは危険。利益確定の検討を。"
        elif score >= 55:
            title = "📊 センチメント「適度な楽観」"
            pendulum = "🎯 振り子は**中立〜やや楽観**"
            desc = f"VIX: **{vix:.1f}** / AAII Bull-Bear: **{aaii_str}**"
            quote = QUOTES['marks']['neutral_ja']
            insight = "トレンドフォローは妥当。ただし過信は禁物。"
        elif score >= 35:
            title = "📊 センチメント「やや悲観」"
            pendulum = "🎯 振り子は**恐怖（Fear）側**に傾いている"
            desc = f"VIX: **{vix:.1f}** / AAII Bull-Bear: **{aaii_str}**"
            quote = QUOTES['marks']['fear_ja']
            insight = "逆張りの準備を始める局面かも。"
        else:
            # 低スコア = 恐怖 = Marks流では「買い場」
            title = "📊 センチメント「恐怖（逆張り好機）」"
            pendulum = "🎯 振り子は**極端な恐怖**に振れている"
            desc = f"VIX: **{vix:.1f}**（高水準）/ AAII Bull-Bear: **{aaii_str}**"
            quote = QUOTES['marks']['fear_ja']
            insight = "長期投資家にとっては「血の流れる路上で買う」絶好の機会かも。"
    else:
        if score >= 75:
            title = "📊 Sentiment: Greed (Caution)"
            pendulum = "🎯 Pendulum swings heavily to **Greed/Optimism**"
            desc = f"VIX: **{vix:.1f}** (low) / AAII Bull-Bear: **{aaii_str}**"
            quote = QUOTES['marks']['greed_en']
            insight = "Risky to pile on when 'everyone is buying.' Consider taking profits."
        elif score >= 55:
            title = "📊 Sentiment: Moderate Optimism"
            pendulum = "🎯 Pendulum at **Neutral to Slightly Optimistic**"
            desc = f"VIX: **{vix:.1f}** / AAII Bull-Bear: **{aaii_str}**"
            quote = QUOTES['marks']['neutral_en']
            insight = "Trend-following is valid. But don't get overconfident."
        elif score >= 35:
            title = "📊 Sentiment: Slightly Pessimistic"
            pendulum = "🎯 Pendulum tilting to **Fear**"
            desc = f"VIX: **{vix:.1f}** / AAII Bull-Bear: **{aaii_str}**"
            quote = QUOTES['marks']['fear_en']
            insight = "May be time to prepare for contrarian plays."
        else:
            title = "📊 Sentiment: Fear (Contrarian Opportunity)"
            pendulum = "🎯 Pendulum swings to **Extreme Fear**"
            desc = f"VIX: **{vix:.1f}** (elevated) / AAII Bull-Bear: **{aaii_str}**"
            quote = QUOTES['marks']['fear_en']
            insight = "May be a golden opportunity to 'buy when there's blood in the streets.'"

    return f"**{title}**\n\n{pendulum}\n\n{desc}\n\n*{quote}*\n\n{insight}"


def suggest_actions(verdict: dict, lang: str) -> str:
    """総合スコアに基づくアクション示唆"""
    score = verdict['verdict_score']
    pillars = verdict.get('pillars', {})
    
    title = t('verdict_why_action_title')
    
    # 各柱のスコア取得
    liq_score = pillars.get('liquidity', {}).get('score', 50)
    sent_score = pillars.get('sentiment', {}).get('score', 50)
    
    if score >= 75:
        if lang == 'ja':
            items = [
                "✅ 流動性・サイクル共に好転 → **株式エクスポージャーを高める好機**",
                "✅ グロース株やシクリカルセクターへの配分を検討",
            ]
            if sent_score >= 70:
                items.append("⚠️ センチメント過熱気味 → 一部利益確定も視野に")
            items.append("📅 次の注目: FOMC、雇用統計、TGA動向")
        else:
            items = [
                "✅ Liquidity & Cycle favorable → **Good time to increase equity exposure**",
                "✅ Consider allocation to Growth and Cyclical sectors",
            ]
            if sent_score >= 70:
                items.append("⚠️ Sentiment overheating → Consider partial profit-taking")
            items.append("📅 Watch: FOMC, NFP, TGA movements")
    elif score >= 45:
        if lang == 'ja':
            items = [
                "🔶 環境は悪くないが、全方位的な強気には慎重に",
                "🔶 業績の裏付けがあるクオリティ株を選別",
                "🔶 押し目買いの方針を維持しつつ、現金比率も確保",
                "📅 次の注目: FOMC、雇用統計の動向を確認",
            ]
        else:
            items = [
                "🔶 Conditions fair, but indiscriminate bullishness is risky",
                "🔶 Select Quality stocks with earnings support",
                "🔶 Maintain 'buy on dip' stance while keeping cash reserves",
                "📅 Watch: FOMC, NFP data releases",
            ]
    else:
        if lang == 'ja':
            items = [
                "🔴 逆風が強まっている → **資本の保全を最優先**",
                "🔴 リスク資産を減らし、債券・ゴールド・現金への避難を検討",
                "🔴 無理にリターンを追わず、嵐が過ぎるのを待つ",
            ]
            if liq_score < 40:
                items.append(f"💧 Howell流: 「流動性が戻るまでじっとしていろ」")
            if sent_score < 35:
                items.append("📊 Marks流: ただし「恐怖の極み」は逆張りチャンスの可能性も")
        else:
            items = [
                "🔴 Headwinds strengthening → **Prioritize capital preservation**",
                "🔴 Reduce risk assets; consider Bonds, Gold, Cash",
                "🔴 Avoid chasing returns; wait for the storm to pass",
            ]
            if liq_score < 40:
                items.append("💧 Howell: 'Stay put until liquidity returns'")
            if sent_score < 35:
                items.append("📊 Marks: Extreme fear may present contrarian opportunities")

    bullet_points = "\n".join([f"• {item}" for item in items])
    return f"**{title}**\n\n{bullet_points}"


def render_why_section(verdict: dict):
    """WHYセクション全体をレンダリング"""
    lang = get_lang()
    pillars = verdict.get('pillars', {})
    
    # セクションタイトル
    st.subheader(t('verdict_why_title'))
    st.caption(t('verdict_why_subtitle'))
    
    # 4本柱の解説カード（2列レイアウト）
    col1, col2 = st.columns(2)
    
    with col1:
        if 'liquidity' in pillars:
            st.info(explain_liquidity(pillars['liquidity']))
        if 'cycle' in pillars:
            st.success(explain_cycle(pillars['cycle']))
            
    with col2:
        if 'technical' in pillars:
            st.warning(explain_technical(pillars['technical']))
        if 'sentiment' in pillars:
            # センチメントの色は状況によって変える
            score = pillars['sentiment'].get('score', 50)
            if score >= 75:  # 過熱（警戒）
                st.error(explain_sentiment(pillars['sentiment']))
            elif score < 35:  # 恐怖（逆張り機会）
                st.success(explain_sentiment(pillars['sentiment']))
            else:
                st.info(explain_sentiment(pillars['sentiment']))
    
    # 免責
    st.caption(t('verdict_why_disclaimer'))
