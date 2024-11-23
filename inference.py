import torch
from torch import nn
import pandas as pd
import pickle 
import argparse
import json

def load_model(model_path):
    if model_path.endswith(".pth"):
        model = torch.load(model_path)
    elif model_path.endswith(".pkl"):
        model = pickle.load(model_path)
    else:
        raise TypeError(f"File type {model_path.split('.')[-1]} cannot be loaded.")
    return model

def inference(model, data):
    if isinstance(model, nn.Module):
        logits = model(data)
        _, pred = torch.max(logits, 1)
        return pred
    else:
        return model.predict(data)
    
def format(prediction):
    # format the output
    return prediction

def parse_data(data):
    if isinstance(data, str):
        df = pd.read_csv(data)

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

    df[['Reporting_Airline', 'Flight_Number_Reporting_Airline']] = df['Flight_Info'].str.split(' ', expand=True)
    df['Flight_Number_Reporting_Airline'] = df['Flight_Number_Reporting_Airline'].astype(float)

    df['Departure Date'] = pd.to_datetime(df['Departure Date'])
    df['Month'] = df['Departure Date'].dt.month

    df['Departure Time'] = pd.to_datetime(df['Departure Time'])
    df['DepTimeBlk'] = df['Departure Time'].dt.hour.apply(lambda h: f"{h:02d}:00-{h:02d}:59")

    df['Arrival Time'] = pd.to_datetime(df['Arrival Time'])
    df['ArrTime'] = df['Arrival Time'].dt.hour * 100 + df['Arrival Time'].dt.minute + 0.0

    df = df.drop(columns=[
        "Departure Date",
        "Airplane",
        "Airline",
        "Departure Latitude",
        "Departure Longitude",
        "Arrival Latitude",
        "Arrival Longitude"
    ])

    with open('all_mappings.json', 'r') as f:
        mapping = json.load('mapping.json') # make sure this file exists somewhere accessible. May need to change path

    df['Origin'] = df['Origin'].map(mapping['Origin']).fillna(-1).astype(int) 
    df['Dest'] = df['Dest'].map(mapping['Dest']).fillna(-1).astype(int) 
    df['Reporting_Airline'] = df['Reporting_Airline'].map(mapping['Reporting_Airline']).fillna(-1).astype(int) 
    df['DepTimeBlk'] = df['DepTimeBlk'].map(mapping['DepTimeBlk']).fillna(-1).astype(int) 
    df['OriginStateName'] = df['OriginStateName'].map(mapping['OriginStateName']).fillna(-1).astype(int) 
    df['DestStateName'] = df['DestStateName'].map(mapping['DestStateName']).fillna(-1).astype(int) 

    return df

def main(model_path, data):
    data = parse_data(data)
    model = load_model(model_path)
    output = inference(model, data)
    return format(output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_path")
    parser.add_argument("data")
    args = parser.parse_args()
    
    main(args)