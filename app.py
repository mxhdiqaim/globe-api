from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # This is important for allowing your frontend to connect

# Endpoint to serve the GeoJSON file
@app.route('/api/cities', methods=['GET'])
def get_cities():
    try:
        # Read the GeoJSON file and return it as JSON
        return send_from_directory('.', 'cities.geojson')
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    # Running the app on port 5000
    app.run(port=5000)