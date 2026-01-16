import pandas_datareader.data as web
import datetime

end = datetime.datetime.now()
start = end - datetime.timedelta(days=730)

# Test various FRED codes
codes = {
    # Core PCE variants
    'PCEPILFE': 'Core PCE Index (current)',
    'PCEPI': 'PCE Index (current)',
    'PCETRIM12M159SFRBDAL': 'Trimmed Mean PCE 12-month',
    
    # ISM variants
    'NAPM': 'ISM Manufacturing (old)',
    'ISM/MAN_PMI': 'ISM Manufacturing PMI',
    'NMFCI': 'Non-Manufacturing ISM current',
    'UMCSENT': 'Consumer Sentiment',
}

for code, desc in codes.items():
    try:
        data = web.DataReader(code, 'fred', start, end, api_key='4e9f89c09658e42a4362d1251d9a3d05')
        if len(data) > 0:
            latest = data.iloc[-1][0]
            date = data.index[-1].strftime('%Y-%m-%d')
            print(f"{code}: {latest:.2f} ({date}) - {desc}")
        else:
            print(f"{code}: NO DATA - {desc}")
    except Exception as e:
        print(f"{code}: ERROR - {str(e)[:50]}")
