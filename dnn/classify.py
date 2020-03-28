import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
import numpy as np
from influxdb import InfluxDBClient
import json
import influxdb
import time
import datetime

client = InfluxDBClient(host='localhost', port=8086,
                        username='admin', password='password')
client.switch_database('timeseriesdb')
i = 0


def classify(mins, i):
    results = {}
    data = []
    df = 0
    predictions = []

    code_timer = time.time()
    query = "SELECT  sr, gs, load, ts, label FROM timeseriesdb.autogen.gear_metrics where time > '{}'".format(
        datetime.datetime.utcnow() - datetime.timedelta(minutes=mins))
    results = client.query(query)
    data = results.raw['series'][0]['values']
    # try:
    #     pass
    # except KeyError as identifier:
    #     print('Database not found. Sleeping 5 ', i)
    #     time.sleep(5)
    #     i += 1
    #     continue
    data = np.array(data)
    df = pd.DataFrame(data=data, columns=[
        "time", "sr", "gs", "load", 'ts', 'label'])

    timestamps = df['ts']
    labels = df['label']

    df = df.drop(['time'], axis=1)
    df = df.drop(['ts'], axis=1)
    df = df.drop(['label'], axis=1)

    # since we can't get real mins and maxes on the
    # fly we will hardcode these values for normalization
    sr_min = 48828.0
    sr_max = 97656.0
    gr_min = -4.0
    gr_max = 3.0
    load_min = 0.0
    load_max = 300.0

    # print(df.head())

    # df = df['SR', 'GR', 'Load']
    df = df.astype(str).astype(float)
    # try:
    #     pass
    # except ValueError as identifier:
    #     print('Value Error caught, skipping iteration ', i)
    #     i += 1
    #     continue

    df['sr'] = df['sr'].apply(
        lambda x: (x - sr_min) / (sr_max - sr_min))

    df['gs'] = df['gs'].apply(
        lambda x: (x - gr_min) / (gr_max - gr_min))

    df['load'] = df['load'].apply(
        lambda x: (x - load_min) / (load_max - load_min))

    new_model = tf.keras.models.load_model('dnn/models/trained_model.h5')

    df = tf.keras.utils.normalize(df, axis=1)

    predictions = new_model.predict(df.values)
    predictions = np.argmax(predictions, axis=1)

    ts_pred = np.stack((timestamps, predictions, labels), axis=-1)

    data = []
    for line in ts_pred:
        # json_line = json.loads(line)
        # Form: 'gear_metrics,metric=offline label=0,sr=97656.0,rate=25.0,gs=0.8407559,load=270.0,timestamp=0'
        data.append("{},metric={} timestamp={},prediction={},label={}".format(
            'labeled_data', 'classification', line[0], line[1], line[2]))

    print('time: ', time.time() - code_timer)
    client.write_points(data, database='timeseriesdb',
                        time_precision='s', batch_size=1, protocol='line')
    print('iteration', i)


while(True):
    i = i + 1
    classify(1, i)
    time.sleep(1*60)
