# Data Quality and Data Wrangling - Scrape the Web Project

This project was a part of the course DLBDSDQDW01 – Data Quality and Data Wrangling at IU University.</br>
The goal for the specific task was to gain experience in the automated gathering of data available online.
As a "setting" the interests of a fictional video game developer were chosen with the goal being to track stats
related to the release of three video games available from December 6th 2024.

<hr style="clear:both;">

## Prerequisites

The code was developed to work during December of 2024, any changes to the respective APIs or websites could have
unplanned consequences for this project.</br>
In an actual live circumstance a developer would then be able to adapt the code accordingly,
but this is beyond the scope of the project, so there is no guarantee that even if all prerequisites are met,
the code will run fine on your local machine.

### Authorization
[RAWG](https://rawg.io/) allows non-commercial use of their API as long as they are attributed as the source.</br>
The [IGDB](https://www.igdb.com/) also allows non-commercial use without express permission request.</br>
Finally the [Steam](https://store.steampowered.com/) API allows for access to and distribution of Steam Data
to end users for personal use, while [SteamCharts](https://steamcharts.com/) themselves don't specify
their usage terms, so it is assumed to be just a different way to view the data available through the Steam API
and follow the same terms and regulations. This project is not affiliated with Valve or Steam.

Please do not use this code without ensuring you have authorization to do so.

#### Keys
To access the different websites, users must add their own respective access tokens to the keys.py file.

### Chromium Driver
The data collection from SteamCharts is based on Google Chrome,
so in order to run the program, you'll need a driver matching your local Chrome installation.
Check [The Chromelabs Page](https://googlechromelabs.github.io/chrome-for-testing/) for the one that matches yours.

<hr style="clear:both;">

## Installation
The application was developed in Python 3.11,
so older versions might not support all functionalities used in the application.
Additionally, in order to run the application,
you will first need to ensure all required packages and modules are installed.
For this you can run the following command in your python terminal.
```shell
pip install -r requirements.txt
```

## Running the Data Collection Application
For running the application which collects new data the following command can be called in the python terminal.
```shell
python main.py
```

<hr style="clear:both;">

## Functionalities
The main application has a single use and runs directly in the python console.

### Updating the Dataset
The program will first ask whether the data should be updated.</br>
Entering "Y" will run the data collection requests. Should a database not have been set up, it will set itself up
based on the information set up in the .csv-Files in the "Sources" folder.</br>
The data is stored in an HDF5-formatted file structured according to the following diagram:</br>

<div align="center">
<img width="100%" src="Sources/HDF5 Structure.png" alt="">
</div>

### Gaining Insights
The collected data can then be further inspected in the analysis.ipnyb Juypter Notebook.
