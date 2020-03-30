import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from influxdb import InfluxDBClient
import json
import influxdb
import time
import datetime
import pickle

client = InfluxDBClient(host='localhost', port=8086,
                        username='admin', password='password')
client.switch_database('timeseriesdb')
i = 0


# pass in the offset from the last run

def classify(offset):
    code_timer = time.time()
    results = {}
    data = []
    predictions = []

    query = "SELECT  sr, gs, load, ts, label FROM timeseriesdb.autogen.gear_metrics where ts > {}".format(
        offset)
    results = client.query(query)
    try:
        data = results.raw['series'][0]['values']
        pass
    except KeyError:
        return offset

    data = np.array(data)
    df = pd.DataFrame(data=data, columns=[
        "time", "sr", "gs", "load", 'ts', 'label'])

    timestamps = df['ts'].astype(str).astype(int).to_numpy()
    print(len(timestamps))
    new_offset = timestamps.max()
    print('new offset: ', new_offset)
    print('points processing: ', int(new_offset) - int(offset))
    labels = df['label'].astype(str).astype(int).to_numpy()
    print(len(labels))

    x = df[['sr', 'gs', 'load']]
    x = x.astype(str).astype(float).to_numpy()  # convert to numpy of floats
    print(len(x))

    model = pickle.load(open("xgboost/model/pima.pickle.dat", "rb"))

    predictions = model.predict(x)  # convert to numpy of floats

    print(len(predictions))

    data = []
    for j in range(len(predictions)):
        # json_line = json.loads(line)
        # Form: 'gear_metrics,metric=offline label=0,sr=97656.0,rate=25.0,gs=0.8407559,load=270.0,timestamp=0'
        data.append("{},metric={} timestamp={},prediction={},label={}".format(
            'labeled_data', 'classification', str(timestamps[j]), str(predictions[j]), str(labels[j])))

    with open('data/test_compare.csv', 'w') as fcsv:
        fcsv.write("sr,gs,load,rate,ts,label\n")
        for line in data:
            fcsv.write(line+"\n")

    client.write_points(data, database='timeseriesdb',
                        time_precision='s', batch_size=100, protocol='line')
    print('time: ', time.time() - code_timer)
    return new_offset


offset = 0
while(True):
    i = i + 1
    print('iteration', i)
    try:
        new_offset = classify(offset)
        pass
    except ValueError as identifier:
        print('Value Error caught, skipping iteration ', i)
        new_offset = offset + 100
        continue
    offset = new_offset
