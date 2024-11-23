from flask import Flask, render_template, request, send_file
import pandas as pd
from serpapi import GoogleSearch
import pickle
import io
import os
from typing import Union
from inference import load_model, inference, format, parse_data  # Imported functions
import json
import torch
## from torch import nn

app = Flask(__name__)

# Load the Decision Tree model at startup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'updated_model.pkl')

try:
    with open(MODEL_PATH, 'rb') as model_file:
        decision_tree_model = pickle.load(model_file)
    print("Model loaded successfully!")
    print(f"Model expected features: {decision_tree_model.feature_names_in_}")
except Exception as e:
    print(f"Error loading model: {e}")
    raise

def inference_combo(model_path: str, data: Union[str, pd.DataFrame]):
    data = parse_data(data)
    print('data ', data)
    model = load_model(model_path)
    print('model ', model)
    output = inference(model, data)
    print('output ', output)
    return data
    #return format(output)

def google_api_search(dep_airport_code, arr_airport_code, dep_date, access_key='43fa493a7a0633b0f8a597de6064f18a9c59373ae5cf15d987f695c487a65c92'):
    params = {
        "engine": "google_flights",
        "departure_id": dep_airport_code.upper(),
        "arrival_id": arr_airport_code.upper(),
        "hl": "en",
        "gl": "us",
        "outbound_date": dep_date,
        "stops": "1",
        "type": "2",
        "api_key": access_key
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        if 'error' in results:
            print(f"ERROR: {results['error']}")
        else:
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
        print("Airport location DataFrame loaded successfully.")

        # Merging departure and arrival airport data
        merged_df = flights_df.merge(
            airport_location_df, left_on='Departure Airport Code', right_on='iata', how='left'
        ).rename(columns={
            'latitude': 'Departure Latitude',
            'longitude': 'Departure Longitude',
            'region_name': 'Departure State'
        }).drop(columns=['country_code', 'icao', 'airport', 'iata'])

        merged_df = merged_df.merge(
            airport_location_df, left_on='Arrival Airport Code', right_on='iata', how='left'
        ).rename(columns={
            'latitude': 'Arrival Latitude',
            'longitude': 'Arrival Longitude',
            'region_name': 'Arrival State'
        }).drop(columns=['country_code', 'icao', 'airport', 'iata'])

        # Add derived features and process data
        merged_df['Day_of_Month'] = pd.to_datetime(merged_df['Departure Date']).dt.day
        merged_df['Day_of_Week'] = pd.to_datetime(merged_df['Departure Date']).dt.dayofweek + 1
        merged_df['AirTime'] = pd.to_numeric(merged_df['Duration'], errors='coerce')
        #merged_df['ArrTime'] = pd.to_datetime(merged_df['Arrival Time'], errors='coerce').dt.hour
        #merged_df['DepTimeBlk'] = pd.cut(
            #pd.to_datetime(merged_df['Departure Time'], errors='coerce').dt.hour,
            #bins=[0, 6, 12, 18, 24],
            #labels=["0000-0559", "0600-1159", "1200-1759", "1800-2359"],
            #include_lowest=True
        #)

        # Now we call the parse_data function to transform the data
        old_df = merged_df
        print(old_df)
        output = inference_combo(MODEL_PATH, merged_df)

    except Exception as e:
        print("Error during API call or data processing:")
        print(e)
        results = None
        merged_df = None

    return results, output

@app.route('/')
def home():
    print("Home route hit.")
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    print("Submit route hit.")
    flight_date = request.form['flight_date']
    airport_origin = request.form['airport_origin']
    airport_destination = request.form['airport_destination']
    print(f"Form data: {flight_date}, {airport_origin}, {airport_destination}")

    results, results_df = google_api_search(airport_origin, airport_destination, flight_date)

    if results_df is not None:
        print("Returning flight data to user.")
        csv = results_df.to_csv(index=False)
        return send_file(io.BytesIO(csv.encode()), mimetype='text/csv', as_attachment=True, download_name='flight_results.csv')
    else:
        print("No results to return.")
        return "No flight information found."

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
