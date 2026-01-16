import pandas_datareader.data as web
import datetime

end = datetime.datetime.now()
start = end - datetime.timedelta(days=730)

# Alternative FRED codes for Global M2
alt_codes = {
    # China M2
    'CN_M2_v1': 'MYAGM2CNM189N',
    'CN_M2_v2': 'MABMM301CNM189S',
    # Japan M2
    'JP_M2_v1': 'MANMM101JPM189S',
    'JP_M2_v2': 'MABMM301JPM189S',
    # EU M2
    'EU_M2_v1': 'MABMM301EZM189S',
    'EU_M2_v2': 'MYAGM2EZM189N',
}

for name, code in alt_codes.items():
    try:
        data = web.DataReader(code, 'fred', start, end, api_key='4e9f89c09658e42a4362d1251d9a3d05')
        if len(data) > 0:
            print(f"{name} ({code}): OK - {len(data)} rows, latest: {data.index[-1].strftime('%Y-%m')}, value: {data.iloc[-1][0]:.1f}")
        else:
            print(f"{name} ({code}): EMPTY")
    except Exception as e:
        print(f"{name} ({code}): ERROR - {str(e)[:50]}")
