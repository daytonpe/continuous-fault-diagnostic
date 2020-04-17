import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from influxdb import InfluxDBClient
import json
import influxdb
import time
import datetime
import pickle
import split_data as sd
import arg_inputs

args = arg_inputs.get_input_args()

client = InfluxDBClient(host='localhost', port=8086,
                        username='admin', password='password')
client.switch_database('timeseriesdb')
i = 0


def classify(offset, DW):
    '''
    offset - integer timestamp from the data generator from which we are to classify
    DW - Data Window size for which we are classifying. I.e. how many readings to classify into a single label

    Classifies the data since the offset timestamp and writes the data to the labeled_data section
    of InfluxDB.
    '''
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
        print('Key Error caught, no values found for this offset. Skipping iteration.')
        return offset

    data = np.array(data)
    df = pd.DataFrame(data=data, columns=[
        "time", "sr", "gs", "load", 'ts', 'label'])

    timestamps = df['ts'].astype(str).astype(int).to_numpy()
    new_offset = timestamps.max()
    print('new offset: ', new_offset)
    print('points processing: ', int(new_offset) - int(offset))
    labels = df['label'].astype(str).astype(int).to_numpy()

    X = df[['sr', 'gs', 'load']].to_numpy()
    # x = x.astype(str).astype(float).to_numpy()  # convert to numpy of floats

    # split data into data window
    X = sd.split_data(DW, X)
    X = np.asarray(X, dtype=np.float32)

    model = pickle.load(open(args.model, "rb"))
    predictions = model.predict(X)  # convert to numpy of floats

    data = []
    for j in range(len(predictions)):
        # Form: 'gear_metrics,metric=offline label=0,sr=97656.0,rate=25.0,gs=0.8407559,load=270.0,timestamp=0'
        data.append("{},metric={} timestamp={},prediction={},label={}".format(
            'labeled_data', 'classification', str(timestamps[j]), str(predictions[j]), str(labels[j])))

    client.write_points(data, database='timeseriesdb',
                        time_precision='s', batch_size=100, protocol='line')
    print('time: ', time.time() - code_timer)
    return new_offset


offset = 0
while(True):
    i = i + 1
    print('\nIteration', i)
    try:
        new_offset = classify(offset, args.dw)
        pass
    except ValueError as identifier:
        print('Value Error caught, skipping iteration ', i)
        time.sleep(1)
        new_offset = offset + 100
        continue
    offset = new_offset
    # sleep for 1 second to minimize ValueErrors by letting some
    # data be produced. Should help for larger DW
    time.sleep(2)
