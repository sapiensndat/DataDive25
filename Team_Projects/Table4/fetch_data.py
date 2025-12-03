import pandas as pd
import requests
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_world_bank_data(indicator, name):
    print(f"Fetching {name} ({indicator}) from World Bank...")
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=10000"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 1:
            records = []
            for entry in data[1]:
                records.append({
                    'country': entry['country']['value'],
                    'countryiso3code': entry['countryiso3code'],
                    'date': entry['date'],
                    'value': entry['value']
                })
            df = pd.DataFrame(records)
            df.to_csv(f"{DATA_DIR}/{name}.csv", index=False)
            print(f"Saved {name}.csv")
        else:
            print("No data found.")
    else:
        print(f"Failed to fetch data: {response.status_code}")

def main():
    # 1. Female Labor Force Participation
    fetch_world_bank_data("SL.TLF.CACT.FE.ZS", "female_labor_force_participation")
    
    # 2. Female Unemployment
    fetch_world_bank_data("SL.UEM.TOTL.FE.ZS", "female_unemployment")

    # 3. Public Sector Employment (Bureaucracy Indicators are often not in standard WDI, trying a proxy or noting manual download)
    # Note: Detailed WWBI data often requires specific CSV downloads, but let's try a common one if available.
    # If not, we rely on the manual instructions.
    print("\nNOTE: Detailed Public Sector employment data (WWBI) often requires manual download.")
    print("Please check data_instructions.md for WWBI and WBES data.")

if __name__ == "__main__":
    main()
