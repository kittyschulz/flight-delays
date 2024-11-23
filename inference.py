import torch
import pandas as pd
import pickle 
import os
import json

from typing import Union

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
    if data.endswith(".csv"):
        df = pd.read_csv(data)
    else:
        df = data

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
        mapping = json.load(f) # make sure this file exists somewhere accessible. May need to change path


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

def main(model_path: str, data: Union[str, pd.DataFrame]):
    data = parse_data(data)
    model = load_model(model_path)
    output = inference(model, data)
    return format(output)