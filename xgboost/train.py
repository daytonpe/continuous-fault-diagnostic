import xgboost as xgb
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split

gear_data = pd.read_csv('data/offline-train-XXL.csv')
gear_data = gear_data.drop('rate', axis=1)
X = gear_data[['sr', 'gs', 'load']]
y = gear_data[['label']]

X_train, X_test, y_train, y_test = train_test_split(
    X.to_numpy(), y.to_numpy().flatten(), test_size=0.3, random_state=101)
print(X_test)

xgboost_model = xgb.XGBClassifier(max_depth=10)

xgboost_model.fit(X_train, y_train,
                  eval_set=[(X_train, y_train), (X_test, y_test)],
                  eval_metric='merror')

pickle.dump(xgboost_model, open("xgboost/model/pima.pickle.dat", "wb"))
