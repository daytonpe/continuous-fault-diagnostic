import xgboost as xgb
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from influxdb import InfluxDBClient
import os
import time
import split_data as sd
import arg_inputs

args = arg_inputs.get_input_args()

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# connect to the TSDB
client = InfluxDBClient(host='localhost', port=8086,
                        username='admin', password='password')
client.switch_database('timeseriesdb')


def retrain(DW, include_offline_data):
    '''
    DW - Data Window size for which we are training. I.e. how many readings to take as a single input to the model
    include_offline_data - should we train using the offline data or just using data that has come in since turning on the classifier

    retrain the model and overwrite the model currently in use.
    '''
    # get the gear_data from the online generated data
    # we found rate to be useless so leave it out
    results = client.query(
        'SELECT  sr, gs, load, ts, label FROM timeseriesdb.autogen.gear_metrics')

    gear_data_online = results.raw['series'][0]['values']
    gear_data_online = np.array(gear_data_online)
    gear_data_online = pd.DataFrame(data=gear_data_online, columns=[
        "datetime", "sr", "gs", "load", 'ts', 'label'])

    X = gear_data_online[['sr', 'gs', 'load']].astype(str).astype(float)
    y = gear_data_online[['label']].astype(str).astype(int)

    if include_offline_data:
        # get the gear_data from the offline generated data
        # right now it's a csv but we could just
        # as easily read it from the offline TDSB
        gear_data_offline = pd.read_csv(args.offline_data)
        gear_data_offline = gear_data_offline.drop('rate', axis=1)
        X_offline = gear_data_offline[['sr', 'gs', 'load']]
        y_offline = gear_data_offline[['label']]

        # add the two sets of data together in order to create a full set
        # on which to train
        X = np.concatenate((X_offline, X), axis=0)
        y = np.concatenate((y_offline, y), axis=0)

    # split data into data window
    X = sd.split_data(DW, X)
    X = np.asarray(X, dtype=np.float32)
    y = sd.split_labels(DW, y)
    y = np.asarray(y, dtype=np.int)

    # split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y.flatten(), test_size=0.3, random_state=101)

    # retrain the classifier
    xgboost_model = xgb.XGBClassifier(max_depth=10, eta=.1)
    xgboost_model.fit(X_train, y_train,
                      eval_set=[(X_train, y_train), (X_test, y_test)],
                      eval_metric='merror')

    # overwrite the original model
    pickle.dump(xgboost_model, open(args.model, "wb"))

    # send out an event to mark when a new data model is created
    data = ["{},metric={} flag={}".format(
        'labeled_data', 'retrain', '1')]

    client.write_points(data, database='timeseriesdb',
                        time_precision='s', batch_size=1, protocol='line')


DW = args.dw
include_offline_data = args.include_offline_data
while (True):
    try:
        retrain(DW, include_offline_data)
    except:
        print('unexpected error. Sleeping for 5 seconds then retrying...')
        time.sleep(5)
        pass
