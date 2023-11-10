import os
import json
import time
import IMDB
import logging
import traceback
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

log_file = 'log_output.txt'

# Create a custom handler for logging that sends messages to the WebSocket
class WebSocketHandler(logging.Handler):
    def emit(self, record):
        log_message = self.format(record)
        socketio.emit('log_message', {'message': log_message}, namespace='/logs')
        with open(log_file, 'a') as f:
            f.write(log_message + '\n')

# Configure the root logger to use the custom handler
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
handler = WebSocketHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root_logger.addHandler(handler)
# Also log to console.
console = logging.StreamHandler()
root_logger.addHandler(console)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_model', methods=['POST'])
def run_model():
    try:
        # data = request.form['model_type']

        # json_data = {
        #     "Model" : data
        # }

        # if data == "LSTM":
        #     epochs = request.form.get('epochs')
        #     batch_size = request.form.get('batch_size')
        #     json_data["Epochs"] = epochs
        #     json_data["Batch Size"] = batch_size

        # json_data = json.dumps(json_data)
        # json_data = json.loads(json_data)

        json_data = request.get_json()

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

@app.route('/logs')
def serve_logs():
    with open(log_file, 'r') as f:
        log_content = f.read()
    return render_template('logs.html', log_content=log_content)

@socketio.on('connect', namespace='/logs')
def connect():
    app.logger.info('Client connected')

@socketio.on('disconnect', namespace='/logs')
def disconnect():
    app.logger.info('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=8081, allow_unsafe_werkzeug=True)