import requests
from datetime import datetime

# --- Auth constants ---
BEARER_TOKEN = "oe_3ZkLc4XUzc1umw2NkKRdpoXL" # This should not be here!
BASE_URL = "https://api.openelectricity.org.au/v4/data/network/NEM"

def _get_mock_electricity_mix():
    # To be more demo friendly, in the event of the API call failing (eg token has expired), return pre-canned data
    # But be sensitive as to whether it is day time (have solar) vs night time (no solar)
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S+10:00")
    
    # Check if it's day time (9am-6pm) or night time
    current_hour = now.hour
    if 9 <= current_hour < 18:
        # Day time
        print("⚠️ get_electricity_mix() falling back to mock data, day time")
        daytime = {
            'power_battery_charging': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 4.5614}, 
            'power_battery_discharging': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 669.3036}, 
            'power_bioenergy': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 79.4644}, 
            'power_coal': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 8980.762}, 
            'power_distillate': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 0.0}, 
            'power_gas': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 548.253}, 
            'power_hydro': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 1015.2095}, 
            'power_pumps': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 0.0}, 
            'power_solar': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 15150.0}, 
            'power_wind': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 4904.5689}
        }
        return daytime
    else:
        # Night time
        print("⚠️ get_electricity_mix() falling back to mock data, night time")
        evening = {
            'power_battery_charging': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 4.5614}, 
            'power_battery_discharging': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 669.3036}, 
            'power_bioenergy': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 79.4644}, 
            'power_coal': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 14980.762}, 
            'power_distillate': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 0.0}, 
            'power_gas': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 2748.253}, 
            'power_hydro': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 3015.2095}, 
            'power_pumps': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 0.0}, 
            'power_solar': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 1.2882}, 
            'power_wind': {'timestamp': '2025-11-03T19:45:00+10:00', 'value': 4904.5689}
        }        
        return evening

def get_electricity_mix():
    try:
        headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

        # For now no limitations on time
        # now = datetime.now(timezone.utc)
        # start = now - timedelta(hours=2)
        # "start": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        # "end": now.strftime("%Y-%m-%dT%H:%M:%S.000Z"),

        fuels = ["coal", "gas", "wind", "solar", "battery_charging", "battery_discharging", "hydro", "distillate", "bioenergy", "pumps"]
        params = {
            "metrics": "power",
            "fueltech_group": fuels
        }

        r = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        

        # The response structure is:
        # {
        #   "version": "...",
        #   "success": true,
        #   "data": [
        #       {
        #           "network_code": "...",
        #           ...
        #           "results": [
        #               {
        #                   "name": "power_coal"
        #                   ...
        #                   "data" [
        #                       [
        #                           "2025-10-16T16:45:00+10:00",
        #                           11861.481
        #                       ]
        #                   ]
        #               }
        #           ]
        #       }
        #   ]
        # }

        # For each fuel type, we want the last data object (most recent)
        payload = r.json()
        data = payload.get("data", [])
        
        
        if not data:
            print("⚠️ get_electricity_mix() no data from API, falling back to mock")
            return _get_mock_electricity_mix()

        # We only want the first element in the data array
        results = data[0]["results"]
        generation_by_source = {}
        for fuel_object in results:
            name = fuel_object["name"]
            data_points = fuel_object.get("data", [])
            if data_points:
                timestamp, value = data_points[-1]
                generation_by_source[name] = {"timestamp": timestamp, "value": value}

        # If we got empty results, fall back to mock
        if not generation_by_source:
            print("⚠️ get_electricity_mix() empty results, falling back to mock")
            return _get_mock_electricity_mix()

        # Sample generation by source
        # {'power_battery_charging': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 78.1957}, 'power_battery_discharging': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 308.2482}, 'power_bioenergy': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 80.1613}, 'power_coal': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 13649.986}, 'power_distillate': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 0.0}, 'power_gas': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 546.0728}, 'power_hydro': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 2294.083}, 'power_pumps': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 0.0}, 'power_solar': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 2315.1695}, 'power_wind': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 6504.6333}}

        #print(f"get_electricity_mix success, {generation_by_source}")
        return generation_by_source
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code in [401, 403, 429]:  # Auth errors or rate limiting
            print(f"🔒 get_electricity_mix() API authentication/authorization error ({e.response.status_code}), using mock data")
        else:
            print(f"⚠️ get_electricity_mix() API HTTP error ({e.response.status_code}), using mock data")
        return _get_mock_electricity_mix()
        
    except requests.exceptions.RequestException as e:
        print(f"🌐 get_electricity_mix() API network error: {e}, using mock data")
        return _get_mock_electricity_mix()
        
    except Exception as e:
        print(f"💥 get_electricity_mix() Unexpected error in get_electricity_mix(): {e}, using mock data")
        return _get_mock_electricity_mix()

# Run a test
#get_electricity_mix()