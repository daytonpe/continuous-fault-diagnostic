# IOT Project 2

## Data Generator

Run the following commands:
`cd iot`
`java -jar datagen-2.2-SNAPSHOT.jar -all`

## Running InfluxDB & Grafana

Assuming you have Docker, Docker CLI, and docker-compose CLI installed you can simply run this command to start the TSDB on port 8086 and the Grafana visualization service at localhost:3000

`docker-compose up`

## Fault Diagnostic Jupyter Notebook

You guys might want to create a new Notebook just so we don't step on each others toes in building our separate parts. But to run the Jupyter notebook suite where I'm building the offline dataset simply run:

`jupyter notebook`
