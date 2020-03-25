import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
import numpy as np
from influxdb import InfluxDBClient
import json
import influxdb

gear_data = pd.read_csv("data/data_predict.csv")

client = InfluxDBClient(host='localhost', port=8086,
                        username='admin', password='password')
client.switch_database('timeseriesdb')
results = client.query(
    'SELECT  sr, gs, load FROM timeseriesdb.autogen.gear_metrics')
data = results.raw['series'][0]['values'][-10000:]
data = np.array(data)
df = pd.DataFrame(data=data, columns=["TIME", "SR", "GR", "Load"])
df = df.drop(['TIME'], axis=1)

cols_to_norm = ['SR', 'GR', 'Load']

df = df[cols_to_norm]
df = df.astype(str).astype(float)

df[cols_to_norm] = df[cols_to_norm].apply(
    lambda x: (x - x.min()) / (x.max() - x.min()))

print('head')
print(df)

sr = tf.feature_column.numeric_column('SR')
gr = tf.feature_column.numeric_column('GR')
load = tf.feature_column.numeric_column('Load')

feat_cols = [sr, gr, load]

new_model = tf.keras.models.load_model('dnn/models/trained_model.h5')

df = tf.keras.utils.normalize(df, axis=1)

new_predictions = new_model.predict(df.values)
for i in new_predictions:
    cl = np.argmax(i)
