import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
import numpy as np
from influxdb import InfluxDBClient


client = InfluxDBClient(host='localhost', port=8086,
                        username='admin', password='password')
client.switch_database('timeseriesdb')

# we found rate to be useless
results = client.query(
    'SELECT  sr, gs, load, ts, label FROM timeseriesdb.autogen.gear_metrics')

data = results.raw['series'][0]['values']
data = np.array(data)
df = pd.DataFrame(data=data, columns=[
                  "datetime", "sr", "gs", "load", 'ts', 'label'])
print(df.head())
df = df.drop(['datetime'], axis=1)
df = df.astype(str).astype(float)
df = df.apply(
    lambda x: (x - x.min()) / (x.max() - x.min()))

cols_to_norm = ['SR', 'GR', 'Load']

sr = tf.feature_column.numeric_column('SR')
rate = tf.feature_column.numeric_column('Rate')
gr = tf.feature_column.numeric_column('GR')
load = tf.feature_column.numeric_column('Load')

feat_cols = [sr, gr, load]

print(df.head())

x_data = df.drop(['label', 'ts'], axis=1)

labels = df['label']

x_train, x_test, y_train, y_test = train_test_split(
    x_data, labels, test_size=0.10, random_state=117)

x_data = tf.keras.utils.normalize(x_data, axis=1)
x_train = tf.keras.utils.normalize(x_train, axis=1)
x_test = tf.keras.utils.normalize(x_test, axis=1)

print('head')
print(x_data.head())

new_model = tf.keras.models.load_model('dnn/models/trained_model.h5')
new_predictions = new_model.predict(x_data.values)

val_loss, val_acc = new_model.evaluate(x_test, y_test)
print(x_train.values.shape)
new_model.fit(x_train.values, y_train.values, epochs=3)
new_model.save('trained_model.h5')
print('accuracy', val_acc)
