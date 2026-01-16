import pandas_datareader.data as web
from datetime import datetime, timedelta

end = datetime.now()
start = end - timedelta(days=730)

# NFP (PAYEMS) - Thousands of Persons
df = web.DataReader('PAYEMS', 'fred', start, end)
print('NFP (PAYEMS):')
print(f'  Rows: {len(df)}')
d = df['PAYEMS'].dropna()
print(f'  Latest: {d.iloc[-1]:,.0f}K')
print(f'  Previous: {d.iloc[-2]:,.0f}K')
print(f'  Monthly Change: {d.iloc[-1] - d.iloc[-2]:+,.0f}K')
print(f'  (Expected: ~+64K based on Japanese source)')

# ADP (ADPWNUSNERSA) - Persons (NOT thousands!)
print()
df2 = web.DataReader('ADPWNUSNERSA', 'fred', start, end)
print('ADP (ADPWNUSNERSA):')
print(f'  Rows: {len(df2)}')
d2 = df2['ADPWNUSNERSA'].dropna()
print(f'  Latest: {d2.iloc[-1]:,.0f} Persons')
print(f'  Previous: {d2.iloc[-2]:,.0f} Persons')
print(f'  Monthly Change: {d2.iloc[-1] - d2.iloc[-2]:+,.0f} Persons')
print(f'  In Thousands: {(d2.iloc[-1] - d2.iloc[-2])/1000:+,.0f}K')

# Average Hourly Earnings
print()
df3 = web.DataReader('CES0500000003', 'fred', start, end)
print('Avg Hourly Earnings (CES0500000003):')
print(f'  Rows: {len(df3)}')
d3 = df3['CES0500000003'].dropna()
print(f'  Latest: ${d3.iloc[-1]:.2f}/hr')
print(f'  Previous: ${d3.iloc[-2]:.2f}/hr')
mom = (d3.iloc[-1] - d3.iloc[-2]) / d3.iloc[-2] * 100
print(f'  MoM change: {mom:+.2f}%')
if len(d3) >= 13:
    yoy = (d3.iloc[-1] - d3.iloc[-13]) / d3.iloc[-13] * 100
    print(f'  YoY change: {yoy:+.2f}%')
