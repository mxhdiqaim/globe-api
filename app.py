from flask import Flask, jsonify
from flask_cors import CORS
import os
import psycopg2
import json

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")

@app.route('/test-db-connection', methods=['GET'])
def test_db():
    try:
        # Use the service name from docker-compose ('db') as the hostname
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"message": f"Successfully connected to PostgreSQL! Version: {db_version}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/load-data', methods=['POST'])
def load_data():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 1. Create a table to store the GeoJSON data
        create_table_query = """
            CREATE TABLE IF NOT EXISTS cities (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            population INTEGER,
            geom GEOMETRY(Point, 4326)
        );
        """
        cur.execute(create_table_query)
        conn.commit()

        # Check if the table is already populated
        cur.execute("SELECT count(*) FROM cities;")
        count = cur.fetchone()[0]
        if count > 0:
            return jsonify({"message": f"Table 'cities' already has {count} entries. Aborting data load."})

        # Read the GeoJSON file
        with open('cities.geojson', 'r') as f:
            geojson_data = json.load(f)

        # Insert each feature into the table
        insert_count = 0
        for feature in geojson_data['features']:
            name = feature['properties']['name']
            population = feature['properties'].get('population', 0)
            geom_json = json.dumps(feature['geometry'])

            insert_query = """
                           INSERT INTO cities (name, population, geom)
                           VALUES (%s, %s, ST_GeomFromGeoJSON(%s)); \
                           """
            cur.execute(insert_query, (name, population, geom_json))
            insert_count += 1

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": f"Successfully loaded {insert_count} cities into the database."})

    except Exception as e:
        if conn:
            conn.rollback()
            if cur:
                cur.close()
            conn.close()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)