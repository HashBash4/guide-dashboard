import requests

# --- Auth constants ---
BEARER_TOKEN = "oe_3ZkLc4XUzc1umw2NkKRdpoXL" # This should not be here!
BASE_URL = "https://api.openelectricity.org.au/v4/data/network/NEM"

def get_electricity_mix():
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
        print("No valid data in API response")
        return None

    # We only want the first element in the data array
    results = data[0]["results"]
    generation_by_source = {}
    for fuel_object in results:
        name = fuel_object["name"]
        data_points = fuel_object.get("data", [])
        if data_points:
            timestamp, value = data_points[-1]
            generation_by_source[name] = {"timestamp": timestamp, "value": value}


    # Sample generation by source
    # {'power_battery_charging': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 78.1957}, 'power_battery_discharging': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 308.2482}, 'power_bioenergy': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 80.1613}, 'power_coal': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 13649.986}, 'power_distillate': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 0.0}, 'power_gas': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 546.0728}, 'power_hydro': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 2294.083}, 'power_pumps': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 0.0}, 'power_solar': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 2315.1695}, 'power_wind': {'timestamp': '2025-10-16T17:20:00+10:00', 'value': 6504.6333}}

    print(f"get_electricity_mix success, {len(generation_by_source)} fuel types")
    return generation_by_source

# Run a test
#get_electricity_mix()