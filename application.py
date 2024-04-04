from flask import Flask, request, render_template_string
import boto3
from botocore.exceptions import BotoCoreError, ClientError

application = Flask(__name__)

# Function to fetch unique Country_Name values and their indexes from DynamoDB table
def get_country_names_and_indexes(table_name):
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        table = dynamodb.Table(table_name)
        response = table.scan(ProjectionExpression="Country_Name, Country_Index")
        sorted_countries = sorted(response['Items'], key=lambda x: x['Country_Index'])
        return sorted_countries
    except (BotoCoreError, ClientError) as e:
        print(f"Error fetching country names and indexes: {e}")
        return []

# Function to fetch data for a specific country from DynamoDB table
def get_country_data(table_name, country_name):
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        table = dynamodb.Table(table_name)
        response = table.scan(FilterExpression="Country_Name = :name", ExpressionAttributeValues={":name": country_name})
        return response['Items']
    except (BotoCoreError, ClientError) as e:
        print(f"Error fetching country data: {e}")
        return []

@application.route('/', methods=['GET', 'POST'])
def display_dropdown():
    table_name = 'QMFS_DATA'
    countries = get_country_names_and_indexes(table_name)
    selected_country_data = []
    if request.method == 'POST':
        selected_country = request.form.get('country')
        selected_country_data = get_country_data(table_name, selected_country)
    
    # Correct the comments in the HTML template part of your Flask application:

    html_template = """
    <!DOCTYPE html>
    <html style="display: flex; flex-direction: column; min-height: 100vh;">
    <head>
        <title>Country Data</title>
        <style>
            body {
                background-color: #b0c4de; /* Metallic Silver Background */
                display: flex;
                flex-direction: column;
                flex: 1;
                margin: 0;
            }
            .footer {
                text-align: center; /* Center the about section */
                margin-top: auto; /* Push the footer to the bottom */
                font-family: 'Georgia', serif; /* Example of a fancier font */
                padding: 20px 0; /* Add some padding */
            }
            table {
                margin: 20px auto; /* Increased spacing around the table */
                border-collapse: collapse;
                width: 60%;
                background-color: #f2f2f2; /* Light grey background */
            }
            th, td {
                border: 1px solid #ddd;
                text-align: left;
                padding: 8px;
            }
            th {
                background-color: #C0C0C0; /* Changed from green to silver */
                color: white;
            }
            #map {
                margin-bottom: 20px; /* Add spacing below the map */
            }
            form {
                margin-bottom: 20px; /* Add spacing below the form */
            }
        </style>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"
            integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A=="
            crossorigin=""/>
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"
            integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA=="
            crossorigin=""></script>
    </head>
    <body>
        <h1 style="text-align: center;">Pick a country, See the data.</h1>
        <div id="map" style="height: 400px;"></div>
        <form method="post" style="text-align: center;">
            <select name="country" onchange="this.form.submit()">
                <option value="">Select Country</option>
                {% for country in countries %}
                    <option value="{{ country['Country_Name'] }}" {% if country['Country_Name'] == selected_country %}selected{% endif %}>{{ country['Country_Name'] }}</option>
                {% endfor %}
            </select>
        </form>
        {% if selected_country_data %}
        <table>
            <tr>
                <th>Field</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Country Name</td>
                <td>{{ selected_country_data[0]['Country_Name'] }}</td>
            </tr>
            <tr>
                <td>Population</td>
                <td>{{ selected_country_data[0]['Population'] }}</td>
            </tr>
            <tr>
                <td>GDP</td>
                <td>{{ selected_country_data[0]['GDP'] }}</td>
            </tr>
            <tr>
                <td>Happiness</td>
                <td>{{ selected_country_data[0]['Happiness_Score'] }}</td>
            </tr>
            <tr>
                <td>Imports</td>
                <td>{{ selected_country_data[0]['Largest_Import'] }}</td>
            </tr>
            <tr>
                <td>Exports</td>
                <td>{{ selected_country_data[0]['Largest_Export'] }}</td>
            </tr>
        </table>
        {% endif %}
            <script>
            var map = L.map('map').setView([20, 0], 2);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors, © CartoDB'
            }).addTo(map);
            var selectedCountryName = "{{ selected_country_data[0]['Country_Name'] if selected_country_data else '' }}";
            if (selectedCountryName) {
                if (selectedCountryName === "United States of America") {
                    var usaLatLng = [39.8283, -98.5795]; // Center of the Continental United States
                    var zoomLevel = 4; // Zoom level for the Continental United States
                    map.setView(usaLatLng, zoomLevel);
                } else {
                    fetch(`https://nominatim.openstreetmap.org/search?country=${selectedCountryName}&format=json&limit=1`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.length > 0) {
                                var lat = data[0].lat;
                                var lon = data[0].lon;
                                var boundingBox = data[0].boundingbox;
                                var southWest = L.latLng(boundingBox[0], boundingBox[2]);
                                var northEast = L.latLng(boundingBox[1], boundingBox[3]);
                                var bounds = L.latLngBounds(southWest, northEast);
                                map.fitBounds(bounds);
                            } else {
                                map.setView([20, 0], 2);
                            }
                        }).catch(error => {
                            console.error('Error fetching geocoding data:', error);
                            alert('Failed to fetch geocoding data for the selected country. Displaying default map view.');
                            map.setView([20, 0], 2);
                        });
                }
            } else {
                map.setView([20, 0], 2);
            }
        </script>
        <div class="footer">
            <p>This project is by Jack Keenan created using Cursor GPT-4, Python Flask, AWS Elastic Beanstalk, AWS DynamoDB, JavaScript, HTML, OpenStreetMap, GeoJSON. Data from World Happiness Report and the World Bank.</p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, countries=countries, selected_country_data=selected_country_data)

if __name__ == "__main__":
    try:
        application.run()
    except Exception as e:
        print(f"Error starting the Flask application: {e}")