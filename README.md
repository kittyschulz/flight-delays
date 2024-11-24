# flight-delays
README.txt - a concise, short README.txt file, corresponding to the "user guide". This file should contain:
## Description
DESCRIPTION - Describe the package in a few paragraphs

The Flask folder contains the templates and code necessary for the website to run. This is how our Flask website is displayed as an html website. Then we have the app.py which is how we run the Flask code. The code app.py uses index.html and mapping.json. In the Flask folder we have the templates folder. The way Flask works you need to have this folder inside the folder you run the Flask python code in. In the templates we have a few htmls, but the only one we ended up using in the final projecct is the index.html. The code inference.py is also in the Flask folder since it is where we took some our code and put it into the app.py. Additionally, we have iata-icao.csv in this folder. This is the data that was used for mapping the airports latitudes, longitudes, names, codes, etc.

Additionally, in the main tree we have a fit_model.py file that will help you recreate our model. We also have the 'Flights Test' tableau dashboard so that you can download that and once running the Flask website code, you can input your data to see what the end user would see if we made this functional and on market. We also have the files for README, license, and requirements.

Other Folders we have are Middle-steps and static/css. The Middle-steps folder contains a lot of the code that we published to each other to make sure we were on the same page and making progress together. The static/css folder was also a Middle-step of when we were thinking of needing this for the formating of the Flask website. 

## Installation
INSTALLATION - How to install and setup your code

To install the Flask website and use the Tableau dashboard, first download the full Flask folder and the 'Flights Test' file. Next, make sure you have all the libraries that the code uses. After, make sure that on your computer you have a "Flask" folder.

## Execution
EXECUTION - How to run a demo on your code

Navigate to that folder and run the app.py code. This should give you an URL to go to use the website. After running this URL make sure you input ALL THREE inputs of date, departure airport, and arrival airport. This will then give you a .csv in a folder inside of your Flask folder. Next open up the Tableau dashboard and update the data that the dashboard is using and you should get a map with flights from your data as well as the pricing, delayed prediction, and general information on what causes flight delays.

## Demo
[Optional, but recommended] DEMO VIDEO - Include the URL of a 1-minute *unlisted* YouTube video in this txt file. The video would show how to install and execute your system/tool/approach (e.g, from typing the first command to compile, to system launching, and running some examples). Feel free to speed up the video if needed (e.g., remove less relevant video segments). This video is optional (i.e., submitting a video does not increase scores; not submitting one does not decrease scores). However, we recommend teams to try and create such a video, because making the video helps teams better think through what they may want to write in the README.txt, and generally how they want to "sell" their work.
[ Embed video here ](link)
