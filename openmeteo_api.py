#!/usr/bin/env python3
import time
import requests
import pandas as pd
from datetime import date, datetime, timedelta

LAT, LON = -33.8688, 151.2093
TIMEZONE = "Australia/Sydney"
START_DATE, END_DATE = date(2023, 10, 13), date(2025, 10, 12)
OUTPUT = f"historic_weather_data_sydney.csv"
URL = "https://archive-api.open-meteo.com/v1/era5"
VARS = ["temperature_2m", "wind_speed_10m", "cloud_cover"]

def month_chunks(s: date, e: date):
    cur = s
    while cur <= e:
        next_month = (cur.replace(day=28) + timedelta(days=4)).replace(day=1)
        last = next_month - timedelta(days=1)
        yield cur, min(last, e)
        cur = last + timedelta(days=1)

def fetch_chunk(s: date, e: date) -> pd.DataFrame:
    params = {
        "latitude": LAT, "longitude": LON,
        "start_date": s.isoformat(), "end_date": e.isoformat(),
        "hourly": ",".join(VARS), "timezone": TIMEZONE,
    }
    for i in range(4):
        r = requests.get(URL, params=params, timeout=60)
        if r.status_code in (429, 500, 502, 503, 504, 414):
            time.sleep(2 ** i); continue
        r.raise_for_status()
        data = r.json().get("hourly", {})
        df = pd.DataFrame(data)
        if df.empty:
            time.sleep(2 ** i); continue
        for v in VARS:
            if v not in df: df[v] = pd.NA
        df["time"] = pd.to_datetime(df["time"], utc=False)
        return df[["time"] + VARS]
    raise RuntimeError(f"Failed {s}—{e}")

def main():
    parts = [fetch_chunk(s, e) for s, e in month_chunks(START_DATE, END_DATE)]
    df = pd.concat(parts, ignore_index=True).drop_duplicates("time").sort_values("time")
    mask = (df["time"] >= pd.Timestamp(START_DATE)) & (df["time"] <= pd.Timestamp(datetime.combine(END_DATE, datetime.max.time())))
    df = df.loc[mask].reset_index(drop=True)
    # rename and convert wind m/s to km/h
    df = df.rename(columns={
        "time": "datetime_local",
        "temperature_2m": "temperature_2m_C",
        "wind_speed_10m": "wind_speed_10m_kmh",
        "cloud_cover": "cloud_cover_pct",
    })
    df["wind_speed_10m_kmh"] = pd.to_numeric(df["wind_speed_10m_kmh"], errors="coerce") * 3.6
    df.to_csv(OUTPUT, index=False)
    print(f"Saved: {OUTPUT}\n", df.head())

if __name__ == "__main__":
    main()