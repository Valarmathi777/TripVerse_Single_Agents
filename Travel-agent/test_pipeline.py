import traceback

try:
    print("1. Testing geocode...")
    from utils.helpers import geocode
    src_lat, src_lon = geocode('Tokyo')
    dst_lat, dst_lon = geocode('Mount Fuji')
    print(f"   Tokyo: {src_lat}, {src_lon}")
    print(f"   Mount Fuji: {dst_lat}, {dst_lon}")
except Exception as e:
    print("FAILED geocode:", traceback.format_exc())

try:
    print("2. Testing weather...")
    from api.weather import get_weather
    w = get_weather(dst_lat, dst_lon)
    print(f"   Weather: {w}")
except Exception as e:
    print("FAILED weather:", traceback.format_exc())

try:
    print("3. Testing traffic...")
    from api.traffic import get_traffic_level
    t = get_traffic_level(src_lat, src_lon)
    print(f"   Traffic: {t}")
except Exception as e:
    print("FAILED traffic:", traceback.format_exc())

try:
    print("4. Testing transport options...")
    from api.transport import get_transport_options
    opts = get_transport_options(src_lat, src_lon, dst_lat, dst_lon, t, 2)
    print(f"   Options: {len(opts)}")
    for o in opts:
        print(f"   - {o['mode']}: {o['duration']}min ${o['cost']}")
except Exception as e:
    print("FAILED transport:", traceback.format_exc())

try:
    print("5. Testing filter...")
    from planner.route_finder import filter_options
    valid = filter_options(opts, 3000, 2, w)
    print(f"   Valid options: {len(valid)}")
except Exception as e:
    print("FAILED filter:", traceback.format_exc())

try:
    print("6. Testing optimizer...")
    from planner.optimizer import optimize_and_recommend
    result = optimize_and_recommend(valid, 'fastest', t, 3000, '08:30')
    print(f"   Result: {result['recommended_mode']} score={result['score']}")
except Exception as e:
    print("FAILED optimizer:", traceback.format_exc())

print("\nDone.")
