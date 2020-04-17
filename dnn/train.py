import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split

# try to supress some of the tensorflow output
tf.logging.set_verbosity(tf.logging.ERROR)

gear_data = pd.read_csv("data/offline-train-M.csv")
print(gear_data.head())

cols_to_norm = ['sr', 'gs', 'load']

gear_data[cols_to_norm] = gear_data[cols_to_norm].apply(
    lambda x: (x - x.min()) / (x.max() - x.min()))

sr = tf.feature_column.numeric_column('sr')
rate = tf.feature_column.numeric_column('rate')
gr = tf.feature_column.numeric_column('gr')
load = tf.feature_column.numeric_column('load')

print(gear_data.head())

feat_cols = [sr, gr, load]

x_data = gear_data.drop(['label', 'rate', 'ts'], axis=1).to_numpy()
y = gear_data[['label']].to_numpy()

x_train, x_test, y_train, y_test = train_test_split(
    x_data, y, test_size=0.3, random_state=101)


x_train = tf.keras.utils.normalize(x_train, axis=1)
x_test = tf.keras.utils.normalize(x_test, axis=1)

print(type(x_train))
print(x_train)

model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.Dense(1024, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(512, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(256, activation=tf.nn.relu))
model.add(tf.keras.layers.Dense(3, activation=tf.nn.softmax))
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(x_train, y_train, epochs=10)

model.save('dnn/models/trained_model.h5')

val_loss, val_acc = model.evaluate(x_test, y_test)
print(val_loss, val_acc)
