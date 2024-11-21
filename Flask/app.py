from flask import Flask, render_template, request, send_file
import serpapi
import pandas as pd
from serpapi import GoogleSearch
import requests
import io
import os


app = Flask(__name__)

def google_api_search(dep_airport_code, arr_airport_code, dep_date, access_key='ffe30b8803eb73dbbe6d2889e77aba0c5023fc74a8c0ebc5886802d17f99397c'):
    params = {
                "engine": "google_flights",
                f"departure_id": {dep_airport_code.upper()},
                f"arrival_id": {arr_airport_code.upper()},
                "hl": "en",
                "gl": "us",
                f"outbound_date": {dep_date},
                "stops": "1",
                "type": "2",
                f"api_key": {access_key}
            }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Print the entire response to debug the structure
        print("API Response:", results)
        
        if 'error' in results:
            print(f"ERROR: {results['error']}")
        else:
            # Check if 'best_flights' and 'other_flights' keys exist
            if 'best_flights' in results:
                results["all_flights"] = results["best_flights"] + results["other_flights"]
            else:
                print("No best_flights found in the response")
                results["all_flights"] = []

        flights = results.get('all_flights', [])
        flight_data = []
        
        for flight in flights:
            flight_info = {
                'Departure Airport Code': dep_airport_code,
                'Arrival Airport Code': arr_airport_code,
                'Departure Date': dep_date,
                'Duration': flight.get('flights', [{}])[0].get('duration', 'Duration not found'),
                'Airplane': flight.get('flights', [{}])[0].get('airplane', 'airplane not found'),
                'Airline': flight.get('flights', [{}])[0].get('airline', 'airline not found'),
                'Flight Number': flight.get('flights', [{}])[0].get('flight_number', 'flight_number not found'),
                'Departure Time': flight.get('flights', [{}])[0].get('departure_airport', {}).get('time', 'depature_time not found'),
                'Arrival Time': flight.get('flights', [{}])[0].get('arrival_airport', {}).get('time', 'arrival_time not found'),
            }
            flight_data.append(flight_info)

        flights_df = pd.DataFrame(flight_data)
        airport_location_df = pd.read_csv('iata-icao.csv')

        merged_df = flights_df.merge(airport_location_df, left_on='Departure Airport Code', right_on='iata', how='left')
        merged_df = merged_df.rename(columns={
            'latitude': 'Departure Latitude',
            'longitude': 'Departure Longitude',
            'region_name': 'Departure State'
        })
        merged_df = merged_df.drop(columns=['country_code','icao', 'airport', 'iata'])

        merged_df = merged_df.merge(airport_location_df, left_on='Arrival Airport Code', right_on='iata', how='left')
        merged_df = merged_df.rename(columns={
            'latitude': 'Arrival Latitude',
            'longitude': 'Arrival Longitude',
            'region_name': 'Arrival State'
        })
        merged_df = merged_df.drop(columns=['country_code', 'icao', 'airport', 'iata'])
        merged_df['Day_of_Month'] = pd.to_datetime(merged_df['Departure Date']).dt.day
        merged_df['Day_of_Week'] = pd.to_datetime(merged_df['Departure Date']).dt.dayofweek
        merged_df['Day_of_Week'] = merged_df['Day_of_Week'] + 1

    except Exception as e:
        print('Error with calling Google API')
        print(e)
        results = None
        merged_df = None

    return results, merged_df


@app.route('/')
def home():
    print("Home route hit")
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    print("Submit route hit")
    # Collect data from the form
    flight_date = request.form['flight_date']
    airport_origin = request.form['airport_origin']
    airport_destination = request.form['airport_destination']
    
    print(f"Form data: {flight_date}, {airport_origin}, {airport_destination}")
    
    results, results_df = google_api_search(airport_origin, airport_destination, flight_date)
    
    if results_df is not None:
        print("Results found")
        # Save the DataFrame to CSV in memory
        csv = results_df.to_csv(index=False)
        # Convert CSV data to a BytesIO object to send as a file
        return send_file(io.BytesIO(csv.encode()), mimetype='text/csv', as_attachment=True, download_name='flight_results.csv')
    else:
        print("No results found")
        return "No flight information found."


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
