import json
import os
import requests
from datetime import datetime
import pytz
import overpy

# Set your local time zone here
LOCAL_TZ = pytz.timezone('America/New_York')  # Replace with your local time zone

# Function to reverse geocode using OpenStreetMap Nominatim
def reverse_geocode(lat, lon):
    base_url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "jsonv2",
        "lat": lat,
        "lon": lon
    }
    headers = {
        "User-Agent": "YourApp/1.0 (https://yourapp.com)"
    }
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        address = data.get('display_name', 'Unknown location')
        return address
    return None

# Function to lookup address using OpenStreetMap Nominatim
def lookup_address(query):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "format": "jsonv2",
        "q": query
    }
    headers = {
        "User-Agent": "YourApp/1.0 (https://yourapp.com)"
    }
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0].get('display_name', 'Unknown location')
    return None

# Function to get POIs using Overpass API
def get_pois(lat, lon, radius=30):
    api = overpy.Overpass()
    query = f"""
    [out:json];
    (
      node["amenity"](around:{radius},{lat},{lon});
      way["amenity"](around:{radius},{lat},{lon});
      relation["amenity"](around:{radius},{lat},{lon});
    );
    out center;
    """
    result = api.query(query)
    pois = []
    for node in result.nodes:
        if node.tags.get('amenity') != 'bench':  # Exclude benches
            pois.append({
                'type': 'node',
                'id': node.id,
                'lat': node.lat,
                'lon': node.lon,
                'tags': node.tags
            })
    for way in result.ways:
        if way.tags.get('amenity') != 'bench':  # Exclude benches
            pois.append({
                'type': 'way',
                'id': way.id,
                'center_lat': way.center_lat,
                'center_lon': way.center_lon,
                'tags': way.tags
            })
    for relation in result.relations:
        if relation.tags.get('amenity') != 'bench':  # Exclude benches
            pois.append({
                'type': 'relation',
                'id': relation.id,
                'center_lat': relation.center_lat,
                'center_lon': relation.center_lon,
                'tags': relation.tags
            })
    return pois

# Function to convert Zulu time to local time
def convert_zulu_to_local(zulu_time_str):
    utc_time = datetime.fromisoformat(zulu_time_str.replace('Z', '+00:00'))
    local_time = utc_time.astimezone(LOCAL_TZ)
    return local_time.isoformat()

# Function to process .rec files
def process_files():
    processed_files = set()
    processed_locations = []

    # Ensure processed_files.txt is created or loaded
    if os.path.exists('processed_files.txt'):
        with open('processed_files.txt', 'r') as f:
            processed_files = set(f.read().strip().split('\n'))
    else:
        open('processed_files.txt', 'a').close()  # Create an empty file if it doesn't exist

    # Get all .rec files in the current directory
    rec_files = [filename for filename in os.listdir('.') if filename.endswith('.rec')]

    # Sort files by name (assuming they are named as year-month.rec)
    rec_files.sort()

    for filename in rec_files:
        # Check if this file has been processed already, skip all but the latest
        if filename in processed_files and filename != rec_files[-1]:
            continue

        print(f"Processing file: {filename}")
        with open(filename, 'r') as file:
            data = file.readlines()
            for line in data:
                try:
                    timestamp, type_, json_data = line.strip().split('\t', 2)
                    location = json.loads(json_data)
                    if location.get('_type') == 'location':
                        if 'lat' not in location or 'lon' not in location or 'tst' not in location:
                            print(f"Skipping record due to missing lat, lon, or tst: {json_data}")
                            continue

                        # Reverse geocode if needed
                        address = reverse_geocode(location['lat'], location['lon'])
                        if not address and 'address_query' in location:
                            address = lookup_address(location['address_query'])
                        location['address'] = address

                        # Get POIs
                        pois = get_pois(location['lat'], location['lon'])
                        location['pois'] = pois

                    location['timestamp'] = convert_zulu_to_local(timestamp)
                    processed_locations.append(location)
                except (ValueError, KeyError) as e:
                    print(f"Skipping line due to error: {e}")
                    continue

        # Mark this file as processed except the last file
        if filename != rec_files[-1]:
            processed_files.add(filename)

    # Save processed filenames to processed_files.txt
    with open('processed_files.txt', 'w') as f:
        f.write('\n'.join(processed_files))

    # Append processed locations to existing processed_locations.json
    existing_locations = []
    if os.path.exists('processed_locations.json'):
        with open('processed_locations.json', 'r') as file:
            existing_locations = json.load(file)

    # Remove duplicates by checking for 'tst', 'lat', and 'lon' keys
    existing_locations_dict = {}
    for loc in existing_locations:
        if 'lat' in loc and 'lon' in loc and 'tst' in loc:
            existing_locations_dict[(loc['tst'], loc['lat'], loc['lon'])] = loc

    for loc in processed_locations:
        if 'lat' in loc and 'lon' in loc and 'tst' in loc:
            existing_locations_dict[(loc['tst'], loc['lat'], loc['lon'])] = loc

    # Save the merged locations back to processed_locations.json
    with open('processed_locations.json', 'w') as file:
        json.dump(list(existing_locations_dict.values()), file, default=str, indent=2)

    print(f"Appended processed locations to processed_locations.json")

if __name__ == "__main__":
    process_files()
