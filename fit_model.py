import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report


def main():
    relative_path = "/content/"
    filename = ['raw_data_v2.pkl']

    try:
        files = [relative_path+x for x in filename]
        for file in files:
            print(file)
            with open(file, 'rb') as f:
                df = pd.read_pickle(f)
    except:
        raise ValueError("Cannot find dataset.")

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

    dt_clf = DecisionTreeClassifier()
    dt_clf.fit(X_train, y_train)

    if eval: 
        preds = dt_clf.predict(X_test)
        print(classification_report(y_test, preds))

    return dt_clf

if __name__=="__main__":
    main()