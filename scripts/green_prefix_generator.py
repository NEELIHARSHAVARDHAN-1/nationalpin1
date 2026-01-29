import json
import math

# DIGIPIN Encoding Logic in Python (matching index.html JS implementation)
def get_digipin(lat, lon):
    LABELLING_GRID = [
        ['F', 'C', '9', '8'],
        ['J', '3', '2', '7'],
        ['K', '4', '5', '6'],
        ['L', 'M', 'P', 'T']
    ]

    min_lat, max_lat = 2.5, 38.50
    min_lon, max_lon = 63.50, 99.50
    
    if not (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon):
        return None

    v_digipin = ""
    lat_div_by, lon_div_by = 4, 4
    
    current_min_lat, current_max_lat = min_lat, max_lat
    current_min_lon, current_max_lon = min_lon, max_lon

    for lvl in range(1, 11):
        lat_div_deg = (current_max_lat - current_min_lat) / lat_div_by
        lon_div_deg = (current_max_lon - current_min_lon) / lon_div_by

        # Find row
        row = 0
        next_max_lat = current_max_lat
        next_min_lat = current_max_lat - lat_div_deg
        for x in range(lat_div_by):
            if lat >= next_min_lat and lat <= next_max_lat:
                row = x
                break
            else:
                next_max_lat = next_min_lat
                next_min_lat = next_max_lat - lat_div_deg

        # Find column
        col = 0
        next_min_lon = current_min_lon
        next_max_lon = current_min_lon + lon_div_deg
        for x in range(lon_div_by):
            if lon >= next_min_lon and lon <= next_max_lon:
                col = x
                break
            elif (next_min_lon + lon_div_deg) < current_max_lon:
                next_min_lon = next_max_lon
                next_max_lon = next_min_lon + lon_div_deg
            else:
                col = x
        
        v_digipin += LABELLING_GRID[row][col]
        if lvl == 3 or lvl == 6:
            v_digipin += "-"
            
        current_min_lat, current_max_lat = next_min_lat, next_max_lat
        current_min_lon, current_max_lon = next_min_lon, next_max_lon
        
    return v_digipin

def generate_sample_points(bbox):
    """
    Generate 11 points: center, 8 extremes, 2 buffers
    bbox: [min_lat, min_lon, max_lat, max_lon]
    """
    min_lat, min_lon, max_lat, max_lon = bbox
    mid_lat = (min_lat + max_lat) / 2
    mid_lon = (min_lon + max_lon) / 2
    
    # Inset for buffers (10%)
    lat_inset = (max_lat - min_lat) * 0.1
    lon_inset = (max_lon - min_lon) * 0.1
    
    points = [
        (mid_lat, mid_lon, "Center"),
        (max_lat, mid_lon, "North"),
        (min_lat, mid_lon, "South"),
        (mid_lat, max_lon, "East"),
        (mid_lat, min_lon, "West"),
        (max_lat, max_lon, "NE"),
        (max_lat, min_lon, "NW"),
        (min_lat, max_lon, "SE"),
        (min_lat, min_lon, "SW"),
        (mid_lat + lat_inset, mid_lon + lon_inset, "Buffer1"),
        (mid_lat - lat_inset, mid_lon - lon_inset, "Buffer2")
    ]
    return points

def fetch_city_boundaries():
    """
    Sample city boundaries for major Indian cities.
    In a real scenario, this would loop through 3000+ cities from a database or OSM.
    """
    # Just a few examples to demonstrate logic
    return [
        {"name": "Hyderabad", "bbox": [17.1, 78.2, 17.6, 78.7]},
        {"name": "Delhi", "bbox": [28.4, 76.8, 28.9, 77.3]},
        {"name": "Mumbai", "bbox": [18.8, 72.7, 19.3, 73.0]},
        {"name": "Bangalore", "bbox": [12.8, 77.4, 13.1, 77.8]},
        {"name": "Chennai", "bbox": [12.9, 80.1, 13.2, 80.3]}
    ]

def analyze_city(city_data):
    points = generate_sample_points(city_data["bbox"])
    prefixes = []
    
    for lat, lon, label in points:
        code = get_digipin(lat, lon)
        if code:
            prefix = code.split('-')[0]
            prefixes.append(prefix)
            
    if not prefixes:
        return None
        
    # Find most common prefix
    counts = {}
    for p in prefixes:
        counts[p] = counts.get(p, 0) + 1
        
    sorted_prefixes = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    green_prefix, count = sorted_prefixes[0]
    coverage = (count / len(prefixes)) * 100
    
    alternatives = [p for p, c in sorted_prefixes[1:] if c > 1]
    
    confidence = "LOW"
    if coverage >= 85: confidence = "VERY_HIGH"
    elif coverage >= 75: confidence = "HIGH"
    elif coverage >= 60: confidence = "MEDIUM"
    
    return {
        "green": green_prefix,
        "coverage": round(coverage, 1),
        "confidence": confidence,
        "alternatives": alternatives
    }

def main():
    cities = fetch_city_boundaries()
    results = {}
    
    print(f"Processing {len(cities)} cities...")
    for city in cities:
        analysis = analyze_city(city)
        if analysis:
            results[city["name"]] = analysis
            print(f"Processed {city['name']}: Green Prefix {analysis['green']} ({analysis['coverage']}%)")
            
    # Save to JSON
    with open('green_prefixes.json', 'w') as f:
        json.dump({
            "metadata": {
                "version": "1.0",
                "total_cities": len(results)
            },
            "cities": results
        }, f, indent=4)
    print("Saved to green_prefixes.json")

if __name__ == "__main__":
    main()
