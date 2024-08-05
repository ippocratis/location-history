from flask import Flask, jsonify, render_template, request
import json
from datetime import datetime

app = Flask(__name__)

# Function to compute stops and their durations
def compute_stops_and_durations(locations):
    stops = []
    threshold_minutes = 20
    
    for i in range(len(locations) - 1):
        current_location = locations[i]
        next_location = locations[i + 1]
        
        # Parse ISO 8601 timestamp format
        current_timestamp = datetime.fromisoformat(current_location['timestamp'])
        next_timestamp = datetime.fromisoformat(next_location['timestamp'])
        
        # Check if the time difference exceeds the threshold
        if (next_timestamp - current_timestamp).total_seconds() / 60 > threshold_minutes:
            stop_duration = next_timestamp - current_timestamp
            stops.append({
                'stop_location': current_location,
                'stop_duration': str(stop_duration)
            })
    
    return stops

# Function to group locations by route based on a time threshold (e.g., 30 minutes)
def groupLocationsByRoute(locations):
    routes = []
    current_route = []
    previous_timestamp = None
    threshold_minutes = 20
    
    for location in locations:
        # Parse ISO 8601 timestamp format
        timestamp = datetime.fromisoformat(location['timestamp'])
        
        if previous_timestamp and (timestamp - previous_timestamp).total_seconds() / 60 > threshold_minutes:
            routes.append(current_route)
            current_route = []
        
        current_route.append(location)
        previous_timestamp = timestamp
    
    if current_route:
        routes.append(current_route)
    
    return routes

# Endpoint to fetch locations based on selected date
@app.route('/get_locations')
def get_locations():
    date = request.args.get('date')
    try:
        with open('processed_locations.json', 'r') as file:
            locations = json.load(file)
            filtered_locations = [loc for loc in locations if loc.get('timestamp', '').startswith(date)]
            return jsonify(filtered_locations)
    except FileNotFoundError:
        return jsonify([])

# New endpoint to search locations based on searchTerm across all dates and filter POIs that are stops
@app.route('/search_locations')
def search_locations():
    searchTerm = request.args.get('searchTerm')
    try:
        with open('processed_locations.json', 'r') as file:
            locations = json.load(file)

            # Group all locations into routes
            grouped_routes = groupLocationsByRoute(locations)

            # Compute stops and durations
            stops_and_durations = compute_stops_and_durations(locations)
            stop_locations = [stop['stop_location'] for stop in stops_and_durations]

            # Filter routes by search term, including only POIs at stop locations
            filtered_routes = [
                route for route in grouped_routes
                if any(
                    searchTerm.lower() in (location.get('address', '') or '').lower() or  # Check address of the location
                    any(
                        searchTerm.lower() in (poi.get('tags', {}).get('name', '') or '').lower() or
                        searchTerm.lower() in (poi.get('tags', {}).get('amenity', '') or '').lower()
                        for poi in location.get('pois', [])  # Iterate over POIs in this location
                    )
                    for location in route  # Iterate over each location in the route
                    if location in stop_locations  # Check if location is a stop
             )   
            ]

            return jsonify(filtered_routes)
    except FileNotFoundError:
        return jsonify([])
    except json.JSONDecodeError:
        return jsonify({'error': 'Error decoding JSON'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New endpoint to fetch all POIs that are stops across all dates
@app.route('/get_all_pois_stops')
def get_all_pois_stops():
    try:
        with open('processed_locations.json', 'r') as file:
            locations = json.load(file)
            
            # Compute stops and durations
            stops_and_durations = compute_stops_and_durations(locations)
            stop_locations = [stop['stop_location'] for stop in stops_and_durations]

            # Collect all POIs from the stop locations
            pois = []
            for location in stop_locations:
                pois.extend(location.get('pois', []))
            
            return jsonify(pois)
    
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Error decoding JSON'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New endpoint to fetch stops and durations based on the selected date
@app.route('/get_stops')
def get_stops():
    date = request.args.get('date')

    # Check if date parameter is provided
    if not date:
        return jsonify({'error': 'Date parameter is required'}), 400

    try:
        with open('processed_locations.json', 'r') as file:
            locations = json.load(file)
            
            # Filter locations based on the date parameter
            filtered_locations = [
                loc for loc in locations 
                if loc.get('timestamp') and loc['timestamp'].startswith(date)
            ]
            
            # Compute stops and durations
            stops_and_durations = compute_stops_and_durations(filtered_locations)
            return jsonify(stops_and_durations)
    
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except json.JSONDecodeError:
        return jsonify({'error': 'Error decoding JSON'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
