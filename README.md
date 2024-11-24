# flight-delays

## Description

The Flask folder contains the templates and code necessary for the website to run. This is how our Flask website is displayed as an html website. Then we have the `app.py` which is how we run the Flask code. The code `app.py` uses `index.html` and `mapping.json`. In the Flask folder we have the templates folder. The way Flask works you need to have this folder inside the folder you run the Flask python code in. In the templates we have a few htmls, but the only one we ended up using in the final project is the index.html. The code `inference.py` is also in the Flask folder since it is where we took some our code and put it into the `app.py`. Additionally, we have `iata-icao.csv` in this folder. This is the data that was used for mapping the airports latitudes, longitudes, names, codes, etc.

Additionally, in the main tree we have a `fit_model.py` file that will help you recreate our model. We also have the `Flights_Test.twbx` tableau dashboard so that you can download that and once running the Flask website code, you can input your data to see what the end user would see if we made this functional and on market. We also have the files for README, license, and requirements.

## Installation

Data is automatically downloaded using the python `gdown` libray from a public location when running our app.

To install the Flask website and use the Tableau dashboard, first download the full Flask folder and the `Flights_Test.twbx` file. Make sure you have all the libraries that the code uses. These are found in `requirements.txt`. 

Make sure that on your computer you have a "Flask" folder. Finally, you will need to download the Decision Tree model from [this link](https://drive.google.com/file/d/1MS93c4DfEhPU4_QS7H-FcfV8-Z7F7sgD/view?usp=sharing). 

## Execution

After cloning this repository, and inside of `flight-delays` directory, run the following:

 ```
 $ cd Flask
 $ python app.py
```

You will see a URL appear in the command line which you should follow to use the website. 

To make your first query, make sure you input ALL THREE inputs of date, departure airport, and arrival airport. This will then give you a `*.csv` file in a folder inside of your Flask folder. Open up the Tableau dashboard and update the data that the dashboard is using and you will get a map with flights from your data as well as the pricing, delayed prediction, and general information on what causes flight delays.

Additionally, the results of the Decision Tree model which are used to make predictions can be reproduced by running `fit_model.py`. A classification report for the performance of the model on the test set will be printed to the console. 

## Demo
Please find the demo video at: [ Demo video ](https://www.youtube.com/watch?v=wjou98-qkBI)

