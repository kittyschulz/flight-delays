import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import gdown
import os
import argparse

import warnings
warnings.filterwarnings("ignore")

def main():
    if not os.path.exists("./raw_data_v2.pkl"):
        print("Downloading sample of dataset to fit model...")
        file_id = '1cYuPB-OmSo9k1Hiy0XM6RgSQHxaWJ_GP'
        url = f'https://drive.google.com/uc?id={file_id}'
        pkl_data = gdown.download(url, None, quiet=True)
    else:
        pkl_data = "./raw_data_v2.pkl"

    try: 
        with open(pkl_data, 'rb') as f:
            df = pd.read_pickle(f)
    except:
        raise ValueError("Cannot find dataset.")

    print("Pre-processing dataset...")
    df.fillna(value=0, inplace=True)
    df["target"] = df[["Cancelled", "Diverted", "ArrDel15"]].any(axis='columns')
    labels = df.pop("target")
    cols = [
        "Origin", 
        "Dest",
        "Month",
        "AirTime",
        "Reporting_Airline",
        "Flight_Number_Reporting_Airline",
        "DepTimeBlk",
        "ArrTime",
        "OriginStateName",
        "DestStateName",
        "DayofMonth",
        "DayOfWeek"
        ]

    training_data = df[cols]
    training_data['Origin'], _ = pd.factorize(training_data['Origin'])
    training_data['Dest'], _ = pd.factorize(training_data['Dest'])
    training_data['Reporting_Airline'], _ = pd.factorize(training_data['Reporting_Airline'])
    training_data['DepTimeBlk'], _ = pd.factorize(training_data['DepTimeBlk'])
    training_data['OriginStateName'], _ = pd.factorize(training_data['OriginStateName'])
    training_data['DestStateName'], _ = pd.factorize(training_data['DestStateName'])

    X_train, X_test, y_train, y_test = train_test_split(
        training_data, labels, test_size=0.33, random_state=42, shuffle=True)

    print("Fitting Decision Tree model...")
    dt_clf = DecisionTreeClassifier()
    dt_clf.fit(X_train, y_train)

    print("Evaluating Decision Tree model...")
    preds = dt_clf.predict(X_test)
    print(classification_report(y_test, preds))
    cm = confusion_matrix(y_test, preds)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot().figure_.savefig('confusion_matrix.png')

    return dt_clf

if __name__=="__main__":
    main()