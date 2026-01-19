
import pandas_datareader.data as web
import datetime

end = datetime.datetime.now()
start = end - datetime.timedelta(days=730)

try:
    data = web.DataReader('MYAGM2CNM189N', 'fred', start, end)
    if data is None or data.empty:
        print("取得結果: 空のデータ (Empty DataFrame)")
    else:
        print("取得成功！")
        print(f"最新データ日付: {data.index[-1]}")
        print(f"最新値: {data.iloc[-1].values[0]}")
except Exception as e:
    print(f"取得失敗: {e}")
