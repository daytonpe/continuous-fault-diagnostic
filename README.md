# Gear Fault Analysis with InfluxDB and XGBoost

- Read generated data from mocked sensors into InfluxDB
- Create an offline data set and train an offline model
- Create a system to continuously read in new data and update the model -- online training
- Display the data, accuracy, and other metrics with Grafana

## Demo

To see a video demonstration of the system in action visit the following YouTube link:
[Gear Fault Analysis with InfluxDB and XGBoost](https://www.youtube.com/watch?v=ANAbMNPWRVA)

## Getting Started

First ensure you have the requirements listed in the `xgboost/requirements.txt` file.

### 1. Start InfluxDB and Grafana Containers

Assuming you have Docker, Docker CLI, and docker-compose CLI installed you can simply run this command to start the TSDB on port 8086 and the Grafana visualization service at localhost:3000

`docker-compose up`

NOTE: this will run continuously so you need to open another console to run the remaining commands.

### 2. Configure Grafana Dashboard

With the Grafana and Influx DB containers running, we will first need to configure Grafana (assuming you want to see visualization metrics). In your browser go to http://localhost:3000 and enter `admin` for both username and password. Change the password to whatever you want if prompted. I've been keeping it as `admin`.

Setup a connection to the running InfluxDB container on the `Add data source` page. If you're using the Docker image from Step 1, simply use the following values:

- url: `http://localhost:8086`
- access: `Browser`
- database: `timeseriesdb`
- user: `admin`
- password: `password`
- HTTP method: `GET`

Leave the rest of the values to their defaults and hit `Save & Test`. You should see a success prompt.

Next hover over the PLUS sign icon on the left under the Grafana logo and select `Import`. Where it says `Or paste JSON` paste in the json from `grafana-dashboard.json` in the repo. Confirm this and then you should be able to pull up the Grafana Dashboard called `Gear Metric Visualization`. These will now begin to populate as soon as you turn on the data generator.

### 3. Create Offline Model

Create the base model from the folling data.

`python xgboost/train.py`

### 4. Starting the Scripts

Open separate console windows for each of the following scripts as they run continuously and asyncronously.

#### 4a. Data Generator

Run the following commands from the root directory to begin producing data:  
`cd iot`

`java -jar datagen-2.4-SNAPSHOT.jar -online`

When this is enabled you should start seeing data populate in the Grafana Dashboard.

#### 4b. Classifier

Begin classifying data windows and writing to Grafana

`python xgboost/classify.py`

#### 4c. Accuracy Calculator

Begin ccalculating accuracy metrics and writing to Grafana

`python xgboost/accuracy.py`

#### 4d. Online Training

Begin online training, continuously retraining and replacing the XGBoost model and writing metrics to Grafana

`python xgboost/retrain.py`

## Tuning the System

The following arguments can be added to the scripts to tune system.

Note: DW must be the same for all scripts that use it or else the system will not run.

- `--dw`, type=int, default=20, data window size in number of measurement
- `--include-offline-data`, type=bool, default=True,if false we will only train based on online data rather than a concatenation of the original offline data and the offline data
- `--offline-data`, type=str, default="data/online-train-XXL.csv", csv of data pulled from offline db for offline training"
- `--mins`, type=int, default=15, rolling minutes for calculating accuracy
- `--model`, type=str, default="xgboost/model/pima.pickle.dat", model to be used for retainging
