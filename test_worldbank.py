import requests
import pandas as pd

# Try EuroZone specific code
countries = {
    'CN': 'China',
    'JP': 'Japan', 
    'EMU': 'Euro Area',  # European Monetary Union
    'XC': 'Euro area',   # Alternative code
}

for code, name in countries.items():
    try:
        url = f"https://api.worldbank.org/v2/country/{code}/indicator/FM.LBL.BMNY.CN?format=json&per_page=5&date=2020:2024"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if len(data) > 1 and data[1]:
            latest = data[1][0]
            if latest['value']:
                print(f"{name} ({code}): {latest['value']:.2e} ({latest['date']})")
            else:
                print(f"{name} ({code}): No value")
        else:
            print(f"{name} ({code}): No data")
    except Exception as e:
        print(f"{name} ({code}): ERROR - {str(e)[:50]}")
