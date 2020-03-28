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

results = client.query(
    'SELECT  prediction, label FROM timeseriesdb.autogen.gear_metrics')
