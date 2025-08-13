from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app) # This is important for allowing your frontend to connect

# Load the GeoJSON data once when the server starts
with open('cities.geojson', 'r') as f:
    ALL_CITIES_DATA = json.load(f)

# Endpoint to serve GeoJSON data based on zoom level
@app.route('/api/cities', methods=['GET'])
def get_cities():
    # Get the altitude parameter from the request URL
    altitude = float(request.args.get('altitude', 1.5))
    
    # Define a simple zoom threshold
    zoom_threshold = 0.6  # This value is relative to the globe's radius

    # If the user is zoomed in enough, return the data
    if altitude < zoom_threshold:
        return jsonify(ALL_CITIES_DATA)
    else:
        # If the user is zoomed out, return an empty GeoJSON
        return jsonify({"type": "FeatureCollection", "features": []})

if __name__ == '__main__':
    # Running the app on port 5000
    app.run(port=5000, debug=True)