import pandas as pd
import tensorflow as tf
import numpy as np
import zipfile
import os
import json
import datetime
import re
import onnx
import tf2onnx
import logging

from flask_socketio import SocketIO
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import classification_report
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from nltk.corpus import stopwords

def clean_text(text, stop_words):
    text = text.lower() # lowercase text
    text = ' '.join(word for word in text.split() if word not in stop_words) # remove stopwords from text
    text = re.sub('<.*?>', ' ', text) # Remove all HTML tags
    text = re.sub(r'\W', ' ', text) # Remove all the special characters
    text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)  # remove all single characters
    text = re.sub(r'\^[a-zA-Z]\s+', ' ', text) # Remove single characters from the start
    text = re.sub(r'\s+', ' ', text, flags=re.I) # Substituting multiple spaces with single space
    return text

def save_model(model, history):
    # Save model summary
    with open("model_summary.txt", "w") as file:
        model.summary(print_fn=lambda x: file.write(x + '\n'))

    # Save fitting progress
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    progress = {
        'timestamp': timestamp,
        'history': history.history
    }
    with open("fitting_progress.json", "w") as file:
        json.dump(progress, file)

def save_report(report):
    # Save report to a file
    with open("accuracy.json", "w") as file:
        json.dump(report, file)

def done_signal():
    # Create a signal file to indicate the program is done
    done_signal = {
        "status": "done"
    }
    with open("done_signal.json", "w") as file:
        json.dump(done_signal, file)

def LSTM_Model(data, epochs, batch_size):
    # The maximum number of words to be used. (most frequent)
    MAX_NB_WORDS = 50000
    # Max number of words in each complaint.
    MAX_SEQUENCE_LENGTH = 250
    # This is fixed.
    EMBEDDING_DIM = 100

    tokenizer = Tokenizer(num_words=MAX_NB_WORDS, filters='!"#$%&()*+,-./:;<=>?@[\]^_`{|}~', lower=True)
    tokenizer.fit_on_texts(data['review'].values)

    X = tokenizer.texts_to_sequences(data['review'].values)
    X = pad_sequences(X, maxlen=MAX_SEQUENCE_LENGTH)
    
    # Converting categorical labels to numbers.
    Y = pd.get_dummies(data['sentiment']).values

    # Train test split
    X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size = 0.2, random_state = 42)
    
    # Define LSTM model
    model = Sequential()
    model.add(Embedding(MAX_NB_WORDS, EMBEDDING_DIM, input_length=X.shape[1]))
    model.add(SpatialDropout1D(0.2))
    model.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dense(2, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    
    # Train the model
    epochs = int(epochs)
    batch_size = int(batch_size)

    history = model.fit(X_train, Y_train, epochs=epochs, batch_size=batch_size, validation_split=0.1)
    y_pred = model.predict(X_test)
    # Convert one-hot encoded labels back to single labels
    Y_test_labels = np.argmax(Y_test, axis=1)
    y_pred_labels = np.argmax(y_pred, axis=1)
    report = classification_report(Y_test_labels, y_pred_labels)
    # accr = model.evaluate(X_test,Y_test)
    # accuracy = {
    #     "Accuracy" : accr[1]
    # }

    save_model(model, history)
    save_report(report)
    
    initial_type = [tf.TensorSpec([None, 250],  tf.int32, name="x")]
    onnx_model, _ = tf2onnx.convert.from_keras(model, initial_type, opset=13)
    onnx.save(onnx_model, "imdb_output.onnx")

    done_signal()

def BoW_Model(x_train, x_test, y_train, y_test):
    vectorizer_BoW = CountVectorizer(binary=True)
    x_train_BoW = vectorizer_BoW.fit_transform(x_train)
    x_test_BoW = vectorizer_BoW.transform(x_test)

    model = LogisticRegression(solver='saga')
    model.fit(x_train_BoW, y_train)
    y_pred_BoW = model.predict(x_test_BoW)
    report = classification_report(y_test, y_pred_BoW)

    # save_model(model, model)
    save_report(report)
    
    initial_type = [("float_input", FloatTensorType([None, 4]))]
    onnx_model = convert_sklearn(model, initial_types=initial_type, target_opset=13)
    onnx.save(onnx_model, "imdb_output.onnx")
    
    done_signal()

def Tfidf_Model(x_train, x_test, y_train, y_test):
    vectorizer_TF = TfidfVectorizer()
    x_train_TF = vectorizer_TF.fit_transform(x_train)
    x_test_TF = vectorizer_TF.transform(x_test)

    model = LogisticRegression(solver='saga')
    model.fit(x_train_TF, y_train)
    y_pred_TF = model.predict(x_test_TF)
    report = classification_report(y_test, y_pred_TF)

    # save_model(model, model)
    save_report(report)
    
    initial_type = [("float_input", FloatTensorType([None, 4]))]
    onnx_model = convert_sklearn(model, initial_types=initial_type, target_opset=13)
    onnx.save(onnx_model, "imdb_output.onnx")
    
    done_signal()

def deploy(json_data):
    DATA_PATH = os.getcwd() + "/IMDB Dataset.csv.zip"

    zf = zipfile.ZipFile(DATA_PATH)
    data = pd.read_csv(zf.open("IMDB Dataset.csv"))

    stop_words = set(stopwords.words('english'))
    excluded_words = set(('never', 'not', 'nor'))
    stop_words = stop_words.difference(excluded_words)
    data['review'] = data['review'].apply(lambda text: clean_text(text, stop_words))

    model = json_data.get("Model")

    if model == "LSTM":
        epochs = json_data["Epochs"]
        batch_size = json_data["Batch Size"]
        LSTM_Model(data, epochs, batch_size)
    else:
        X = data['review'].values
        sentiment_mapping = {'negative': 0, 'positive': 1}
        y = data['sentiment'].map(sentiment_mapping)
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        if model == "BoW":
            BoW_Model(x_train, x_test, y_train, y_test)
        elif model == "TF-IDF":
            Tfidf_Model(x_train, x_test, y_train, y_test)