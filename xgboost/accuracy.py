import pandas as pd
import sklearn
from sklearn import metrics
import numpy as np
from influxdb import InfluxDBClient
import datetime
import time
import arg_inputs

# connect to the TSDB
client = InfluxDBClient(host='localhost', port=8086,
                        username='admin', password='password')
client.switch_database('timeseriesdb')
i = 0


# Get the accuracy over the last 15 minutes

def calc_accuracy(mins):
    results = {}
    data = []
    predictions = []

    query = "SELECT label, prediction FROM timeseriesdb.autogen.labeled_data where time > '{}'".format(
        datetime.datetime.utcnow() - datetime.timedelta(minutes=mins))

    results = client.query(query)
    try:
        data = results.raw['series'][0]['values']
        pass
    except KeyError:
        return

    df = pd.DataFrame(data=data, columns=[
        "time", "label", "prediction"])

    labels = df['label'].astype(str).astype(int).to_numpy()
    predictions = df['prediction'].astype(str).astype(int).to_numpy()

    accuracy = sklearn.metrics.accuracy_score(
        labels, predictions, normalize=True, sample_weight=None)

    data = ["{},metric={} norm_acc={}".format(
        'labeled_data', 'accuracy', str(accuracy))]

    client.write_points(data, database='timeseriesdb',
                        time_precision='s', batch_size=1, protocol='line')
    print(accuracy)


args = arg_inputs.get_input_args()
while(True):
    try:
        calc_accuracy(args.mins)
        time.sleep(5)
        pass
    except ValueError as identifier:
        print('Value Error caught, skipping iteration ', i)
        continue
