import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
import numpy as np
from influxdb import InfluxDBClient
import json
import influxdb
import time

client = InfluxDBClient(host='localhost', port=8086,
                        username='admin', password='password')
client.switch_database('timeseriesdb')

i = 0

while (True):
    code_timer = time.time()
    results = client.query(
        'SELECT  sr, gs, load, ts FROM timeseriesdb.autogen.gear_metrics order by desc limit 10000')
    data = results.raw['series'][0]['values']
    data = np.array(data)
    df = pd.DataFrame(data=data, columns=["TIME", "SR", "GR", "Load", 'ts'])

    timestamps = df['ts']

    df = df.drop(['TIME'], axis=1)
    df = df.drop(['ts'], axis=1)

    cols_to_norm = ['SR', 'GR', 'Load']

    df = df[cols_to_norm]
    try:
        df = df.astype(str).astype(float)
        pass
    except ValueError as identifier:
        print('Value Error caught, skipping iteration ', i)
        i += 1
        continue

    df[cols_to_norm] = df[cols_to_norm].apply(
        lambda x: (x - x.min()) / (x.max() - x.min()))

    new_model = tf.keras.models.load_model('dnn/models/trained_model.h5')

    df = tf.keras.utils.normalize(df, axis=1)

    predictions = new_model.predict(df.values)
    predictions = np.argmax(predictions, axis=1)
    ts_pred = np.stack((timestamps, predictions), axis=-1)

    data = []
    for line in ts_pred:
        # json_line = json.loads(line)
        # Form: 'gear_metrics,metric=offline label=0,sr=97656.0,rate=25.0,gs=0.8407559,load=270.0,timestamp=0'
        data.append("{},metric={} timestamp={},label={}".format(
            'labeled_data', 'classification', line[0], line[1]))

    client.write_points(data, database='timeseriesdb',
                        time_precision='s', batch_size=10000, protocol='line')
    i = i + 1
    print('iteration', i)
    print('time: ', time.time() - code_timer)
