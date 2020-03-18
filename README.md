# IOT Project 2

## Data Generator

Run the following commands:
`cd iot;`
`java -jar datagen-1.0-SNAPSHOT.jar -all`

## Running InfluxDB

Assuming you have Docker, Docker CLI, and docker-compose CLI installed you can simply run this command to start the TSDB on port 8086

`docker-compose up timeseriesdb`

## Fault Diagnostic Jupyter Notebook

You guys might want to create a new Notebook just so we don't step on each others toes in building our separate parts. But to run the Jupyter notebook suite where I'm building the offline dataset simply run:

`jupyter notebook`
