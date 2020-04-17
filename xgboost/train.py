import xgboost as xgb
import pandas as pd
import numpy as np
import pickle
import split_data as sd
from sklearn.model_selection import train_test_split
import arg_inputs

args = arg_inputs.get_input_args()

gear_data = pd.read_csv(args.offline_data)
gear_data = gear_data.drop('rate', axis=1)
X = gear_data[['sr', 'gs', 'load']].to_numpy()
y = gear_data[['label']].to_numpy()

print('X', X)
print('y', y)

# split data into data window
DW = args.dw
X = sd.split_data(DW, X)
X = np.asarray(X, dtype=np.float32)
y = sd.split_labels(DW, y)
y = np.asarray(y, dtype=np.int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=101)

xgboost_model = xgb.XGBClassifier(max_depth=10, eta=.1)

xgboost_model.fit(X_train, y_train,
                  eval_set=[(X_train, y_train), (X_test, y_test)],
                  eval_metric='merror')

pickle.dump(xgboost_model, open(args.model, "wb"))
