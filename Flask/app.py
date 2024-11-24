from flask import Flask, render_template, request, send_file
import serpapi
import pandas as pd
from serpapi import GoogleSearch
import requests
import io
import os
import pickle
import csv
import torch
from torch import nn
import argparse
import gdown
import json
from typing import Union
import random

app = Flask(__name__)

OUTPUT_FOLDER = "Flight Results"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def load_model(model_path):
    if model_path.endswith(".pth"):
        model = torch.load(model_path)
    elif model_path.endswith(".pkl"):
        with open(model_path , 'rb') as f:
            model = pickle.load(f)
    else:
        raise TypeError(f"File type {model_path.split('.')[-1]} cannot be loaded.")
    return model

def inference(model, data):
    if isinstance(model, torch.nn.Module):
        logits = model(data)
        _, pred = torch.max(logits, 1)
        return pred
    else:
        return model.predict(data)
    
def format(prediction):
    # format the output
    return prediction

def parse_data(data):
    if isinstance(data, str):  # If data is a string (file path)
        df = pd.read_csv(data)
    elif isinstance(data, pd.DataFrame):  # If data is already a DataFrame
        df = data
    else:
        raise TypeError("Input data must be a string (file path) or a pandas DataFrame.")
    
    # Proceed with renaming columns and further processing
    df = df.rename(columns={
        'Departure Airport Code': 'Origin', 
        'Arrival Airport Code': 'Dest',
        'Duration': 'AirTime',
        'Arrival Time': 'ArrTime',
        'Departure State': 'OriginStateName',
        'Arrival State': 'DestStateName',
        'Day_of_Month': 'DayofMonth',
        'Day_of_Week': 'DayOfWeek',
    })

    df[['Reporting_Airline', 'Flight_Number_Reporting_Airline']] = df['Flight Number'].str.split(' ', expand=True)
    df['Flight_Number_Reporting_Airline'] = df['Flight_Number_Reporting_Airline'].astype(float)

    df['Departure Date'] = pd.to_datetime(df['Departure Date'])
    df['Month'] = df['Departure Date'].dt.month

    df['Departure Time'] = pd.to_datetime(df['Departure Time'])
    df['DepTimeBlk'] = df['Departure Time'].dt.hour.apply(lambda h: f"{h:02d}:00-{h:02d}:59")

    df['ArrTime'] = pd.to_datetime(df['ArrTime'])
    df['ArrTime'] = df['ArrTime'].dt.hour * 100 + df['ArrTime'].dt.minute + 0.0

    df = df.drop(columns=[
        "Flight Number",
        "Departure Date",
        "Departure Time",
        "Airplane",
        "Airline",
        "Departure Latitude",
        "Departure Longitude",
        "Arrival Latitude",
        "Arrival Longitude"
    ])

    with open('mapping.json', 'r') as f:
        mapping = json.load(f)

    df['Origin'] = df['Origin'].map(mapping['Origin']).fillna(-1).astype(int) 
    df['Dest'] = df['Dest'].map(mapping['Dest']).fillna(-1).astype(int) 
    df['Reporting_Airline'] = df['Reporting_Airline'].map(mapping['Reporting_Airline']).fillna(-1).astype(int) 
    df['DepTimeBlk'] = df['DepTimeBlk'].map(mapping['DepTimeBlk']).fillna(-1).astype(int) 
    df['OriginStateName'] = df['OriginStateName'].map(mapping['OriginStateName']).fillna(-1).astype(int) 
    df['DestStateName'] = df['DestStateName'].map(mapping['DestStateName']).fillna(-1).astype(int) 

    desired_order = [
        'Origin', 'Dest', 'Month', 'AirTime', 'Reporting_Airline', 
        'Flight_Number_Reporting_Airline', 'DepTimeBlk', 'ArrTime', 
        'OriginStateName', 'DestStateName', 'DayofMonth', 'DayOfWeek'
    ]
    df = df[desired_order]

    return df

def google_api_search(dep_airport_code, arr_airport_code, dep_date, access_key='43fa493a7a0633b0f8a597de6064f18a9c59373ae5cf15d987f695c487a65c92'):
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
        if 'error' in results:
            print(f"ERROR: {results['error']}")
        else:
            results["all_flights"] = results["best_flights"] + results["other_flights"]

        flights = results.get('all_flights', [])
        flight_data = []
        
        price_insights = results.get('price_insights', {})
        typical_price_range = price_insights.get('typical_price_range', ['Not available', 'Not available'])
        
        
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
                'Price': flight.get('price', 'Price not found'),
                'Typical Price Range (Low)': typical_price_range[0],
                'Typical Price Range (High)': typical_price_range[1]
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
        
        merged_df['Adjusted_Departure_Latitude'] = merged_df['Departure Latitude'] + [
            random.uniform(-1, 1) for _ in range(len(merged_df))
        ]

        merged_df['Adjusted_Departure_Longitude'] = merged_df['Departure Longitude']  # Keep longitude the same

        merged_df['Adjusted_Arrival_Latitude'] = merged_df['Arrival Latitude'] + [
            random.uniform(-1, 1) for _ in range(len(merged_df))
        ]

        merged_df['Adjusted_Arrival_Longitude'] = merged_df['Arrival Longitude'] 

    except Exception as e:
        print('Error with calling Google API')
        print(e)
        results = None
        merged_df = None

    return results, merged_df

def recover_uid(df):
    mapping = {"Reporting_Airline":  {"9E": 0, "AA": 1, "AS": 2, "B6": 3, "DL": 4, "F9": 5, "G4": 6, "HA": 7, "MQ": 8, "NK": 9, "OH": 10, "OO": 11, "UA": 12, "WN": 13, "YX": 14, "QX": 15, "YV": 16}}
    reverse_mapping = {v: k for k, v in mapping["Reporting_Airline"].items()}
    df['Reporting_Airline'] = df['Reporting_Airline'].map(reverse_mapping)
    df['Flight_Number'] = df['Reporting_Airline'] + ' ' + df['Flight_Number_Reporting_Airline'].astype(int).astype(str)
    #df['Flight_Number'] = df['Reporting_Airline'].astype(str) + ' ' + df['Flight_Number_Reporting_Airline'].astype(str)
    print(df)
    return df

@app.route('/')
def home():
    print("Home route hit")
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        print("Submit route hit")
        # Collect data from the form
        flight_date = request.form['flight_date']
        airport_origin = request.form['airport_origin']
        airport_destination = request.form['airport_destination']

        # Call the Google API with the form inputs
        results, merged_df = google_api_search(airport_origin, airport_destination, flight_date)
        
        #os.system("!gdown '1MS93c4DfEhPU4_QS7H-FcfV8-Z7F7sgD' ")
        # Download model
        #gdown.download('https://drive.google.com/file/d/1MS93c4DfEhPU4_QS7H-FcfV8-Z7F7sgD', 'updated_model.pkl', quiet=False)
        model_path = os.path.join('updated_model.pkl')
        
        data = parse_data(merged_df)
        model = load_model(model_path)
        output = inference(model, data)
        
        data['Predictions'] = output
        mapping = {True: 'Delayed', False: 'On Time'}
        data['Predictions'] = data['Predictions'].map(mapping)
        data = recover_uid(data)
        
        merged_df['Predictions'] = merged_df['Flight Number'].map(data.set_index('Flight_Number')['Predictions'])
        
        if merged_df is not None:
            print("Results found, writing to CSV")
            csv_file_path = os.path.join(OUTPUT_FOLDER, 'flights_data.csv')
            merged_df.to_csv(csv_file_path, mode='w', index=False, header=True)
            
            print("DataFrame column types:\n", merged_df.dtypes)

            return f"Flight information successfully saved to {csv_file_path}"

        else:
            print("No results found")
            return render_template('error.html', error_message="No flight information found.")
    except Exception as e:
        print("Error occurred:", e)
        return render_template('error.html', error_message=str(e))



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
