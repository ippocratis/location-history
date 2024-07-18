# **Location History**

"Location history" aims to be a location history visualizer that offers search (city, region, state, address,postal code),a date picker,day navigation arrows, route grouping and a map to visualize routes and location pins..

## Backend

On the backend side , app.py Python code defines a Flask web application with several functionalities related to processing and retrieving location data.

Here’s a breakdown:

- Initialization of Flask Application:

app = Flask(__name__) initializes the Flask web application.

- Function to Group Locations by Route:

The function groupLocationsByRoute(locations) takes a list of locations, each containing a timestamp, and groups them into routes based on a time threshold (30 minutes).
If the time difference between consecutive locations exceeds the threshold, a new route is started.

- Endpoint to Fetch Locations by Date:

The endpoint /get_locations accepts a date parameter (e.g., YYYY-MM-DD format) as a query string.
It reads processed_locations.json to get the list of locations.
It filters the locations to return only those whose timestamps start with the specified date.

- Endpoint to Search Locations by Term:

The endpoint /search_locations accepts a searchTerm parameter.
It reads processed_locations.json to get the list of locations.
It uses groupLocationsByRoute to group all locations into routes.
It filters the routes to include only those where any location's address contains the search term (case-insensitive).

- Homepage Route:

The endpoint / renders an index.html template, which would be the homepage of the web application.
Running the Application:

The application runs in debug mode and listens on all available IP addresses (host='0.0.0.0').

# Data gathering, reverse geocode and handling:

### Owntracks:

- For location tracking i use owntracks.
It is a location tracking app.
It logs coordinates when the android device moves.Locations are saved in json files with a .rec extention.
What differs owntracks from other tracking apps is that it waits for the smart phone to tell it that the device has moves only then can OwnTracks react.
It then needs a server to connect to. Basic http server can be used . I have configured a more advanced set up , connecting to an mqtt broker using mutual TLS . For setting up the owntracks recorder (the server) read.

https://ippocratis.github.io/owntracks/ 


## The prepropcess.py python script:

Process .rec files containing location data, reverse geocode the locations using the OpenStreetMap Nominatim service, and save the processed data to processed_locations JSON file.

Here’s a breakdown:

- Reverse Geocode Function (reverse_geocode):

Inputs: Latitude (lat), Longitude (lon).
Output: Address as a string.
Functionality: Sends a GET request to the Nominatim reverse geocoding API to convert latitude and longitude into a human-readable address.

- Lookup Address Function (lookup_address):

Input: Address query (query).
Output: Address as a string.
Functionality: Sends a GET request to the Nominatim search API to find the address based on a search query.

###  Process Files Function:

- Processes all .rec files in the current directory, extracts location data, and performs reverse geocoding.

- Load Processed Files:
Checks and loads processed_files.txt to keep track of already processed files.


- Retrieve .rec Files:
Lists and sorts all .rec files in the current directory.

- Process Each .rec File:
For each file, unless it has been processed already (excluding the latest one), it reads and processes the data.
Each line is expected to have a timestamp, a type, and JSON data.
Parses the JSON data, extracts latitude, longitude, and timestamp.
Performs reverse geocoding to obtain the address.
Adds the timestamp in ISO format to the location data.

- Save Processed Files:
Updates processed_files.txt to mark files as processed.
Merge and Save Processed Locations:
Loads existing locations from processed_locations.json.
Merges new locations with existing ones, ensuring no duplicates based on tst (timestamp), lat, and lon.
Saves the updated locations back to processed_locations.json.


# Frontend

### index.html

- Controls Section: Contains a search input for locations, date navigation buttons, and a date picker.

- Map Container: Holds the map where routes and locations will be displayed.

- Timeline Section: Displays a timeline of routes.

- Search Results Popup: A modal popup to display search results


- The date selection fill the timeline container with routes.

- Location inclusion in a route made so that locations within a 30 min span belong to the same route.

- Timeline routes are expandable.Selecting a route entry in timeline displaying it as a directional polyline on the map.
Expanded route locations entries are name/time taged.

- Search resaults routes  are selectable. Clicking on them display the route on the map

- Search input also dominates the timeline . If it is filled only matched routes are displayed in the timeline .

# Run the app

- Put preprocess.py app.py requirements.txt the .rec files on root Dir and index.html in templates/index.html then run "python app.py" and open index.html

Or

- Put Dockerfile docker-compose.yml entrypoint.sh together with preprocess.py app.py requirements.txt and the .rec files on root Dir and index.html in templates/index.html and run "docker compose up --build -d" app is running on localhost on port 8789 but you can refine your port in docker-compose.

- Or simply clone this repo and run "docker compose up --build -d"

- A copy_files.py is also added in this repo . You could fill the source and destination dir for .rec files and run it periodically in a cronjob.

- Running the docker compose file will first run the preprocess.py script , you can comment that line in entrypoint.sh if you don't want the script to run every time docker compose is starting .
  
- Handle reverse proxy and SSL certs mtls in your webserver if you plan to expose the app outside your localhost.
  
