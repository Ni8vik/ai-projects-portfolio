import tensorflow as tf
import keras
import matplotlib.pyplot as plt
import numpy as np

#datasets
(X_train, Y_train) , (X_test, Y_test) = keras.datasets.mnist.load_data()

X_train = X_train / 255
X_test = X_test / 255

X_train_flattend = X_train.reshape(len(X_train),28*28)
X_test_flattend = X_test.reshape(len(X_test),28*28)


#model
model = keras.Sequential([
      keras.layers.Dense(100, input_shape=(784,), activation="relu"),
      keras.layers.Dense(75, input_shape=(100,), activation="tanh"),
      keras.layers.Dense(10, activation="sigmoid")
])
#compiler
model.compile(
      optimizer="adam"
      ,loss="sparse_categorical_crossentropy"
      ,metrics=["accuracy"])

#saver
model_checkpoint = "nueral network/handwriten/hwd.model.weights.h5"
cp_callback = keras.callbacks.ModelCheckpoint(model_checkpoint,
                                              save_weights_only=True,
                                              verbose=1)

#model.load_weights(model_checkpoint)
model.fit(X_train_flattend, Y_train, epochs=15,
          callbacks= [cp_callback])

model.evaluate(X_test_flattend, Y_test)

plt.matshow(X_test[2])
plt.matshow(X_test[1])
plt.matshow(X_test[0])
plt.show()
y_predicted =model.predict(X_test_flattend)
y_predicted_labels = [np.argmax(i) for i in y_predicted[:3]]#for multiple items
print(y_predicted_labels)
