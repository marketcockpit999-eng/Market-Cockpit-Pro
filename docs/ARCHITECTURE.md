# Market Cockpit Pro - Architecture

## Entry Point
- `market_app_nav.py` - Main Streamlit app

## Pages (UI)
- `pages/01_liquidity.py` - Fed liquidity & rates
- `pages/02_global_money.py` - Global M2 & FX
- `pages/03_us_economic.py` - US economic indicators
- `pages/04_crypto.py` - Crypto metrics
- `pages/05_ai_analysis.py` - AI market summary
- `pages/06_monte_carlo.py` - Monte Carlo simulation
- `pages/07_market_voices.py` - Market news
- `pages/08_sentiment.py` - Sentiment indicators
- `pages/09_banking.py` - Banking sector

## Utils (Logic)
- `utils/config.py` - 🔑 SINGLE SOURCE OF TRUTH for all configs (imports from indicators.py)
- `utils/indicators.py` - 🔑 INDICATOR DEFINITIONS REGISTRY
- `utils/data_fetcher.py` - Data fetching (FRED, Yahoo, CMC, etc.)
- `utils/charts.py` - Charting functions
- `utils/helpers.py` - UI helper functions (if exists, or merged)
- `utils/ai_clients.py` - Gemini/Claude API clients
- `utils/data_processor.py` - Data processing logic

## Data Flow
1. User opens app → `market_app_nav.py`
2. `get_market_data()` called → `utils/data_fetcher.py`
3. Indicators defined in → `utils/indicators.py`
4. Data stored in session_state
5. Pages access via `st.session_state['df']`
