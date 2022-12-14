# -*- coding: utf-8 -*-
"""MLOPS_Model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rK9Bsjs1XlnCWssI0NRCyNK9tGigDbO6
"""

import sys
import numpy as np
from keras import layers, models
from keras.datasets import imdb
import matplotlib.pyplot as plt

"""Constants"""

MAX_WORDS  = 1000
BATCH_SIZE = 500
EPOCHS = 10

"""Importing data"""

(training_data, training_targets), (testing_data, testing_targets) = imdb.load_data(
        num_words=MAX_WORDS
    )
data = np.concatenate((training_data, testing_data), axis=0)
targets = np.concatenate((training_targets, testing_targets), axis=0)
sample = data[0].copy()

vectorized_data = np.zeros((len(data), MAX_WORDS))
for i, sequence in enumerate(data):
  vectorized_data[i, sequence] = 1
data = vectorized_data
targets = np.array(targets).astype("float32")

    # split datset (leave first 1000 rows for validation testing)
test_x = data[1000:10000]
test_y = targets[1000:10000]
train_x = data[10000:]
train_y = targets[10000:]


sample

index = imdb.get_word_index()
reverse_index = dict([(value, key) for (key, value) in index.items()]) 
decoded = " ".join( [reverse_index.get(i - 3, "#") for i in sample] )
decoded

"""Building the model"""

model = models.Sequential()
model.add(layers.Dense(50, activation="relu", input_shape=(MAX_WORDS,)))
model.add(layers.Dropout(0.3, noise_shape=None, seed=None))
model.add(layers.Dense(100, activation="relu"))
model.add(layers.Dropout(0.3, noise_shape=None, seed=None))
model.add(layers.Dense(50, activation="relu"))
model.add(layers.Dense(1, activation="sigmoid"))
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
model.summary()

"""Train"""

history = model.fit(
    train_x,
    train_y,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    validation_data=(test_x, test_y),
)

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""Saving model"""

model.save("./saved_model")