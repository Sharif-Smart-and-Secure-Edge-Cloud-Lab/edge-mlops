import os
import json
import time
import IMDB
import traceback
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_model', methods=['POST'])
def run_model():
    try:
        data = request.form['model_type']

        json_data = {
            "Model" : data
        }

        if data == "LSTM":
            epochs = request.form.get('epochs')
            batch_size = request.form.get('batch_size')
            json_data["Epochs"] = epochs
            json_data["Batch Size"] = batch_size

        json_data = json.dumps(json_data)
        json_data = json.loads(json_data)

        IMDB.deploy(json_data)

        while not os.path.isfile('done_signal.json'):
            # Wait for the signal file to be created
            time.sleep(1)

        # Signal file exists, read the results
        # with open('fitting_progress.json', 'r') as fp:
            # fitting_progress = json.load(fp)

        with open('accuracy.json', 'r') as fp:
            accuracy = json.load(fp)

        # Remove the signal file to prepare for the next run
        os.remove('done_signal.json')

        return jsonify({'result': accuracy})
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='localhost', port=8081)