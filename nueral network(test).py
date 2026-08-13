import tensorflow as tf
import keras
import matplotlib.pyplot as plt
import numpy as np

(X_train, Y_train) , (X_test, Y_test) = keras.datasets.mnist.load_data()

X_train = X_train / 255
X_test = X_test / 255

X_train_flattend = X_train.reshape(len(X_train),28*28)
X_test_flattend = X_test.reshape(len(X_test),28*28)

model = keras.Sequential([
      keras.layers.Dense(100, input_shape=(784,), activation="relu"),
      keras.layers.Dense(10, activation="sigmoid")
])

model.compile(
      optimizer="adam"
      ,loss="sparse_categorical_crossentropy"
      ,metrics=["accuracy"])

model.fit(X_train_flattend, Y_train, epochs=5)

model.evaluate(X_test_flattend, Y_test)


y_predicted =model.predict(X_test_flattend)
y_predicted_labels = [np.argmax(i) for i in y_predicted[:3]]
print(y_predicted_labels)
