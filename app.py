from flask import Flask, jsonify, render_template, request
import json
from datetime import datetime

app = Flask(__name__)

# Function to group locations by route based on a time threshold (e.g., 30 minutes)
def groupLocationsByRoute(locations):
    routes = []
    current_route = []
    previous_timestamp = None
    threshold_minutes = 30
    
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

# New endpoint to search locations based on searchTerm across all dates
@app.route('/search_locations')
def search_locations():
    searchTerm = request.args.get('searchTerm')
    try:
        with open('processed_locations.json', 'r') as file:
            locations = json.load(file)
            
            # Group all locations into routes
            grouped_routes = groupLocationsByRoute(locations)
            
            # Filter routes by search term
            filtered_routes = [
                route for route in grouped_routes 
                if any(
                    searchTerm.lower() in (loc.get('address', '') or '').lower() or 
                    any(
                        searchTerm.lower() in (poi.get('tags', {}).get('name', '') or '').lower() or 
                        searchTerm.lower() in (poi.get('tags', {}).get('amenity', '') or '').lower()
                        for poi in loc.get('pois', [])
                    )
                    for loc in route
                )
            ]
            
            return jsonify(filtered_routes)
    except FileNotFoundError:
        return jsonify([])




@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
