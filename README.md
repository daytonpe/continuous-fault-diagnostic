# IOT Project 2

## Getting Started

### 1. Start InfluxDB and Grafana Containers

Assuming you have Docker, Docker CLI, and docker-compose CLI installed you can simply run this command to start the TSDB on port 8086 and the Grafana visualization service at localhost:3000

`docker-compose up`

### 2. (Optional) Configure Grafana Dashboard

With the Grafana and Influx DB containers running, we will first need to configure Grafana (assuming you want to see visualization metrics). In your browser go to http://localhost:3000 and enter `admin` for both username and password. Change the password to whatever you want if prompted. I've been keeping it as `admin`.

Setup a connection to the running InfluxDB container on the `Add data source` page.

- url: `http://localhost:8086`
- access: `Browser`
- database: `timeseriesdb`
- user: `admin`
- password: `password`
- HTTP method: `GET`

Leave the rest of the values to their defaults and hit `Save & Test`. You should see a success prompt.

Next hover over the PLUS sign icon on the left under the Grafana logo and select `Import`. Where it says `Or paste JSON` paste in the json from `grafana-dashboard.json` in the repo. Confirm this and then you should be able to pull up the Grafana Dashboard called `Gear Metric Visualization`. These will now begin to populate as soon as you turn on the data generator.

### 3. Data Generator

Run the following commands from the root directory:  
`cd iot`

`java -jar datagen-2.2-SNAPSHOT.jar -online`

## Fault Diagnostic Jupyter Notebook

You guys might want to create a new Notebook just so we don't step on each others toes in building our separate parts. But to run the Jupyter notebook suite where I'm building the offline dataset simply run:

`jupyter notebook`

Currently I've just been using this notebook to perform basic queries and drop the db before new runs.
