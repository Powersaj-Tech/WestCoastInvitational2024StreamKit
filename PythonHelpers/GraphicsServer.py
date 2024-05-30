from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import eventlet

app = Flask(__name__)
CORS(app)  # Enable CORS on all routes
socketio = SocketIO(app, cors_allowed_origins="*")

active_message = "Initial message"
counter = 0
VolPosition = "VolPosition"
VolName = "VolName"
VolTeamNum = "VolTeamNum"


def background_thread():  # test function that updates the text every ms
    global counter
    while True:
        #socketio.sleep(0.001) #1ms
        socketio.sleep(1)
        counter += 1
        socketio.emit('active_message', {'message': 'Webhook Updates: ' + str(counter) + ' Server Interval: 1s'},
                      namespace='/GetActiveMessage')


@socketio.on('connect', namespace='/GetActiveMessage')
def get_active_message():
    print("Client connected")
    emit('active_message', {'message': active_message})


@app.route('/UpdateMessageCall/<msg>')
def update_message_call(msg):
    global active_message
    active_message = msg
    socketio.emit('active_message', {'message': active_message}, namespace='/GetActiveMessage')
    print("Message updated: " + active_message)
    return jsonify({'result': 'Message updated', 'message': active_message})


@app.route('/UpdateVolPositionCall/<pos>/<name>/<team>')
def update_vol_position_call(pos, name, team):
    global VolPosition, VolName, VolTeamNum
    VolPosition = pos
    VolName = name
    VolTeamNum = team
    socketio.emit('active_vols', {'VolPosition': VolPosition, 'VolName': VolName, 'VolTeamNum': VolTeamNum},
                  namespace='/GetActiveVols')
    print("Volunteer Position updated: " + VolPosition + " " + VolName + " " + VolTeamNum)
    return jsonify({'result': 'Volunteer Position updated', 'VolPosition': VolPosition, 'VolName': VolName,
                    'VolTeamNum': VolTeamNum})


@socketio.on('connect', namespace='/GetActiveVols')
def get_active_vols():
    print("Client connected")
    emit('active_vols', {'VolPosition': VolPosition, 'VolName': VolName, 'VolTeamNum': VolTeamNum})


if __name__ == '__main__':
    socketio.start_background_task(background_thread)
    socketio.run(app, port=4444)
