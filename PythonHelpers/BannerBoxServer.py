from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import eventlet

app = Flask(__name__)
CORS(app)  # Enable CORS on all routes
socketio = SocketIO(app, cors_allowed_origins="*")

active_message = "Initial message"
counter = 0


def background_thread():  # test function that updates the text every ms
    global counter
    while True:
        socketio.sleep(0.001)
        counter += 1
        socketio.emit('active_message', {'message': 'Server Call Counter: ' + str(counter) + ' Server Interval: 1ms'},
                      namespace='/GetActiveMessage')


@app.route('/UpdateMessageCall/<msg>')
def update_message_call(msg):
    global active_message
    active_message = msg
    socketio.emit('active_message', {'message': active_message}, namespace='/GetActiveMessage')
    print("Message updated: " + active_message)
    return jsonify({'result': 'Message updated', 'message': active_message})


@socketio.on('connect', namespace='/GetActiveMessage')
def get_active_message():
    print("Client connected")
    emit('active_message', {'message': active_message})


if __name__ == '__main__':
    socketio.start_background_task(background_thread)
    socketio.run(app, port=4444)
