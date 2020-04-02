from influxdb import InfluxDBClient

# delete the db and rebuild it.
client = InfluxDBClient(host='localhost', port=8086,
                        username='admin', password='password')
client.drop_database('timeseriesdb')
client.query('create database timeseriesdb with duration 1d')
client.switch_database('timeseriesdb')
