import pandas as pd
import zipfile
import os
import json
import datetime
import re

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import classification_report
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
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

def Sentiment(text, analyzer):
    score = analyzer.polarity_scores(text)['compound']
    if (score >= 0):
        return 'Positive'
    elif (score < 0):
        return 'Negative'
    # else :      if needed
    #     return 'Neutral'

def LSTM_Model(data):
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
    epochs = 2
    batch_size = 128

    history = model.fit(X_train, Y_train, epochs=epochs, batch_size=batch_size, validation_split=0.1)
    accr = model.evaluate(X_test,Y_test)
    accuracy = {
        "Accuracy" : accr[1]
    }

    save_model(model, history)
    save_report(accuracy)
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
    done_signal()

def Sentiment_Model(data):
    analyzer = SentimentIntensityAnalyzer()

    data['sentiment'] = data['review'].apply(lambda x: Sentiment(x, analyzer))
    
    negative = data.loc[data['sentiment'] == 'Negative']
    positive = data.loc[data['sentiment'] == 'Positive']
    negative_true = negative.loc[data['sentiment'] == 'Negative']
    positive_true = positive.loc[data['sentiment'] == 'Positive']

    precision_0 = len(negative_true) / len(negative)
    precision_1 = len(positive_true) / len(positive)

    report = {
        'precision_0': precision_0,
        'precision_1': precision_1
    }

    save_report(report)
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
        LSTM_Model(data)
    else:
        X = data['review'].values
        sentiment_mapping = {'negative': 0, 'positive': 1}
        y = data['sentiment'].map(sentiment_mapping)
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        if model == "BoW":
            BoW_Model(x_train, x_test, y_train, y_test)
        elif model == "TF-IDF":
            Tfidf_Model(x_train, x_test, y_train, y_test)
        elif model == "Sentiment":
            Sentiment_Model(data)