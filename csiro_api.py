import requests
from datetime import datetime, timedelta, timezone
import pytz

# --- Auth constants ---
CLIENT_ID = "f89cc48b-27bc-4593-b71e-cb9c79396277"
CLIENT_SECRET = "vc68Q~aZjKUdSyNzu1X0GFJnKyWMQ85DmBEHGcGf"
TENANT_ID = "a815c246-a01f-4d10-bc3e-eeb6a48ef48a"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

OBS_URL = "https://senaps.eratos.com/api/sensor/v2/observations"
STREAM_ID = "csiro.energy.dch.agshop.regional_global_emissions.nsw"

def get_token():
    """Retrieve OAuth token."""
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": f"{CLIENT_ID}/.default",
    }
    r = requests.post(TOKEN_URL, data=data, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]

def get_latest_intensity():
    """Return the most recent carbon intensity value (gCO2/kWh)."""
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=2)

    params = {
        "streamid": STREAM_ID,
        "start": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "end": now.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "limit": 1,
        "sort": "desc",
    }

    r = requests.get(OBS_URL, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    results = r.json().get("results", [])
    if not results:
        return None

    sydney_tz = pytz.timezone("Australia/Sydney")
    entry = results[0]
    utc_time = datetime.strptime(entry["t"], "%Y-%m-%dT%H:%M:%S.000Z").replace(tzinfo=timezone.utc)
    sydney_time = utc_time.astimezone(sydney_tz)
    value = entry["v"]["v"]
    return sydney_time, value
