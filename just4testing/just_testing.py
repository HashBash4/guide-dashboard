import requests
from datetime import datetime, timedelta, timezone
import pytz
import pandas as pd
import time

# --- Auth constants ---
CLIENT_ID = "f89cc48b-27bc-4593-b71e-cb9c79396277"
CLIENT_SECRET = "vc68Q~aZjKUdSyNzu1X0GFJnKyWMQ85DmBEHGcGf"
TENANT_ID = "a815c246-a01f-4d10-bc3e-eeb6a48ef48a"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

OBS_URL = "https://senaps.eratos.com/api/sensor/v2/observations"
STREAM_ID = "csiro.energy.dch.agshop.regional_global_emissions.nsw"


# --- Token ---
def get_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": f"{CLIENT_ID}/.default",
    }
    r = requests.post(TOKEN_URL, data=data, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]


# --- Query function for a given time window ---
def get_emissions_data(token, start, end):
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "streamid": STREAM_ID,
        "start": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "limit": 9999999,
    }

    r = requests.get(OBS_URL, headers=headers, params=params, timeout=60)
    r.raise_for_status()
    results = r.json().get("results", [])
    return results


# --- Get 2 years of hourly carbon intensity ---
def get_hourly_intensity_two_years():
    token = get_token()
    print("✅ Token obtained.")

    sydney_tz = pytz.timezone("Australia/Sydney")
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=365 * 2)

    all_data = []

    # We’ll request data month by month to avoid overload
    current_start = start_date
    while current_start < now:
        current_end = min(current_start + timedelta(days=31), now)
        print(f"📅 Fetching {current_start.date()} to {current_end.date()}...")
        try:
            results = get_emissions_data(token, current_start, current_end)
            for entry in results:
                utc_time = datetime.strptime(entry["t"], "%Y-%m-%dT%H:%M:%S.000Z").replace(tzinfo=timezone.utc)
                sydney_time = utc_time.astimezone(sydney_tz)
                value = entry["v"]["v"]
                all_data.append((sydney_time, value))
        except Exception as e:
            print("⚠️ Error fetching data:", e)

        # Move to next month
        current_start = current_end
        time.sleep(0.3)  # small delay between requests

    # --- Convert to DataFrame ---
    df = pd.DataFrame(all_data, columns=["datetime", "intensity_gCO2_per_kWh"])
    df = df.sort_values("datetime")

    # --- Resample hourly ---
    df.set_index("datetime", inplace=True)
    df_hourly = df.resample("1H").mean().dropna()

    print(f"✅ Retrieved {len(df_hourly)} hourly records from {df_hourly.index.min().date()} to {df_hourly.index.max().date()}")
    return df_hourly


if __name__ == "__main__":
    df_hourly = get_hourly_intensity_two_years()
    df_hourly.to_csv("nsw_hourly_carbon_intensity.csv")
    print("💾 Saved to nsw_hourly_carbon_intensity.csv")
