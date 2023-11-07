import os
import json
import time
import IMDB
import logging
import traceback
from flask import Flask, request, jsonify, render_template, Response

app = Flask(__name__)

log_file = 'log_output.txt'

# Configure the root logger to write log messages to the file
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create a file handler to write log messages to the log file
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

# Also log to console
console = logging.StreamHandler()
console.setFormatter(formatter)
root_logger.addHandler(console)

# Create a generator function to stream log updates
def stream_logs():
    with open(log_file, 'r') as log:
        while True:
            # Read new log lines
            new_lines = log.readlines()
            if new_lines:
                yield f"data: {''.join(new_lines)}\n\n"
            time.sleep(1)  # Adjust the refresh rate as needed

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
        app.logger.error(str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/<model_type>')
@app.route('/<model_type>/<int:epochs>/<int:batch_size>')
def run_model_from_url(model_type, epochs=None, batch_size=None):
    try:
        json_data = {
            "Model" : model_type
        }

        if model_type == "LSTM" and epochs is not None and batch_size is not None:
            json_data["Epochs"] = epochs
            json_data["Batch Size"] = batch_size

        json_data = json.dumps(json_data)
        json_data = json.loads(json_data)

        IMDB.deploy(json_data)

        while not os.path.isfile('done_signal.json'):
            # Wait for the signal file to be created
            time.sleep(1)

        with open('accuracy.json', 'r') as fp:
            accuracy = json.load(fp)

        # Remove the signal file to prepare for the next run
        os.remove('done_signal.json')

        return jsonify({'result': accuracy})
    
    except Exception as e:
        app.logger.error(str(e))
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/logs')
def serve_logs():
    return Response(stream_logs(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run(host='localhost', port=8081)