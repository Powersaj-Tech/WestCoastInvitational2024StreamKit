import requests
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

names = {
    "1": "Volunteer Name 1",
    "2": "Volunteer Name 2",
    "3": "Volunteer Name 3",
    "4": "Volunteer Name 4",
    "5": "Volunteer Name 5"
}

position = {
    "1": "Volunteer Position 1",
    "2": "Volunteer Position 2",
    "3": "Volunteer Position 3",
    "4": "Volunteer Position 4",
    "5": "Volunteer Position 5"
}

teams = {
    "1": "Team Number 1",
    "2": "Team Number 2",
    "3": "Team Number 3",
    "4": "Team Number 4",
    "5": "Team Number 5"
}

currentperson = 1


def getPerson():
    global currentperson
    currentperson += 1
    if currentperson > names.__len__():
        currentperson = 1
    return position[str(currentperson)], names[str(currentperson)], teams[str(currentperson)]


def background_thread():  # test function that updates the text every ms
    global counter
    global VolPosition, VolName, VolTeamNum
    while True:
        #socketio.sleep(0.001) #1ms
        socketio.sleep(1 / 30)
        counter += 1
        socketio.emit('active_message', {'message': 'Webhook Updates: ' + str(counter) + ' Server Interval: 30tps'},
                      namespace='/GetActiveMessage')
        if counter % 40 == 0:
            VolPosition, VolName, VolTeamNum = getPerson()
            socketio.emit('active_vols', {'VolPosition': VolName, 'VolName': VolPosition, 'VolTeamNum': VolTeamNum},
                          namespace='/GetActiveVols')


@socketio.on('connect', namespace='/GetActiveMessage')
def get_active_message():
    emit('active_message', {'message': active_message})


@app.route('/UpdateMessageCall/<msg>')
def update_message_call(msg):
    global active_message
    active_message = msg
    socketio.emit('active_message', {'message': active_message}, namespace='/GetActiveMessage')
    return jsonify({'result': 'Message updated', 'message': active_message})


@app.route('/UpdateVolPositionCall/<pos>/<name>/<team>')
def update_vol_position_call(pos, name, team):
    global VolPosition, VolName, VolTeamNum
    VolPosition = pos
    VolName = name
    VolTeamNum = team
    socketio.emit('active_vols', {'VolPosition': VolPosition, 'VolName': VolName, 'VolTeamNum': VolTeamNum},
                  namespace='/GetActiveVols')
    return jsonify({'result': 'Volunteer Position updated', 'VolPosition': VolPosition, 'VolName': VolName,
                    'VolTeamNum': VolTeamNum})


@socketio.on('connect', namespace='/GetActiveVols')
def get_active_vols():
    emit('active_vols', {'VolPosition': VolPosition, 'VolName': VolName, 'VolTeamNum': VolTeamNum})


if __name__ == '__main__':
    socketio.start_background_task(background_thread)
    socketio.run(app, port=4444)
