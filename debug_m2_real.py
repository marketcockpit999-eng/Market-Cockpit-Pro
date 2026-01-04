import pandas as pd
import pandas_datareader.data as web
import datetime

FRED_API_KEY = "4e9f89c09658e42a4362d1251d9a3d05"
end = datetime.datetime.now()
start = end - datetime.timedelta(days=730)

print("=== M2 (Real) Debug Script ===\n")

# Fetch data
print("Fetching FRED data...")
m2 = web.DataReader('M2SL', 'fred', start, end, api_key=FRED_API_KEY)
cpi = web.DataReader('CPIAUCSL', 'fred', start, end, api_key=FRED_API_KEY)

# Combine
df = pd.concat([m2, cpi], axis=1).sort_index()
df.columns = ['M2SL', 'CPI']

print("\n=== Original Data (Millions) ===")
print(df.tail(3))
print(f"\nM2SL Latest: {df['M2SL'].iloc[-1]:,.1f} million")

# Unit conversion (millions to billions)
df['M2SL'] = df['M2SL'] / 1000

print("\n=== After Unit Conversion (Billions) ===")
print(df.tail(3))
print(f"\nM2SL Latest: {df['M2SL'].iloc[-1]:.4f} B")

# Calculate Real M2
cpi_base = df['CPI'].dropna().iloc[0]
print(f"\nCPI Base (2 years ago): {cpi_base:.3f}")

df['US_Real_M2_Index'] = (df['M2SL'] / df['CPI'].ffill()) * cpi_base

print("\n=== After Real M2 Calculation ===")
print(df[['M2SL', 'CPI', 'US_Real_M2_Index']].tail(3))
print(f"\nUS_Real_M2_Index Latest: {df['US_Real_M2_Index'].iloc[-1]:.4f} B")

# Verify calculation
latest_m2 = df['M2SL'].iloc[-1]
latest_cpi = df['CPI'].ffill().iloc[-1]
expected_real = (latest_m2 / latest_cpi) * cpi_base
print(f"\n=== Calculation Verification ===")
print(f"M2SL: {latest_m2:.4f} B")
print(f"CPI: {latest_cpi:.3f}")
print(f"Real M2 = ({latest_m2:.4f} / {latest_cpi:.3f}) * {cpi_base:.3f}")
print(f"Real M2 = {expected_real:.4f} B")

print("\n=== Expected Values ===")
print("M2 (Nominal): 22.3 B")
print("M2 (Real): 21.3 B")
