import requests
from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import eventlet
import random
import time
import threading
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS on all routes
socketio = SocketIO(app, cors_allowed_origins="*")

tps = 15

active_message = "Initial message"
counter = 0
VolPosition = "VolPosition"
VolName = "VolName"
VolTeamNum = "VolTeamNum"
TeamNum = "TeamNum"
WinningTeam = "WinningTeam" # Red or Blue
ActivateWin = "false"
countdowntime = time.time() + 1210

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


def background_thread():
    while True:
        socketio.sleep(3.5)
        socketio.emit('active_team', {'TeamNumber': str(random.randint(10000, 60000))},
            namespace='/GetActiveTeam')

def volunteer_thread():
    global VolPosition, VolName, VolTeamNum
    while True:
        socketio.sleep(5)
        VolPosition, VolName, VolTeamNum = getPerson()
        socketio.emit('active_vols', {'VolPosition': VolName, 'VolName': VolPosition, 'VolTeamNum': VolTeamNum},
            namespace='/GetActiveVols')

def timer_thread():
    while True:
        countdown = countdowntime - time.time()
        minutes = str(int(countdown / 60))
        seconds = int(countdown % 60)
        if seconds < 10:
            seconds = "0" + str(seconds)
        else:
            seconds = str(seconds)
        socketio.emit('active_message', {'message': minutes + ":" + seconds}, namespace='/GetActiveMessage')
        socketio.sleep(1)


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

@app.route('/UpdateWinResultCall/<result>/<color>')
def update_win_result_call(result, color):
    global ActivateWin, WinningTeam
    ActivateWin = result
    WinningTeam = color
    socketio.emit('win_result', {'WinResult': ActivateWin, 'WinColor': WinningTeam}, namespace='/GetWinResult')
    return jsonify({'result': 'Win Result updated', 'WinResult': ActivateWin, 'WinColor': WinningTeam})

@app.route('/UpdateTeamNumberCall/<team>')
def update_team_number_call(team):
    global TeamNum
    TeamNum = team
    socketio.emit('active_team', {'TeamNumber': TeamNum}, namespace='/GetActiveTeam')
    return jsonify({'result': 'Team Number updated', 'TeamNumber': TeamNum})

@socketio.on('connect', namespace='/GetActiveMessage')
def get_active_message():
    print('connected to /GetActiveMessage')
    emit('active_message', {'message': active_message})


@socketio.on('connect', namespace='/GetActiveVols')
def get_active_vols():
    print('connected to /GetActiveVols')
    emit('active_vols', {'VolPosition': VolPosition, 'VolName': VolName, 'VolTeamNum': VolTeamNum})


@socketio.on('connect', namespace='/GetActiveTeam')
def get_active_team():
    print('connected to /GetActiveTeam')
    emit('active_team', {'TeamNumber': TeamNum})

@socketio.on('connect', namespace='/GetWinResult')
def get_win_result():
    print('connected to /GetWinResult')
    emit('win_result', {'WinResult': ActivateWin, 'WinColor': WinningTeam})


if __name__ == '__main__':
    socketio.start_background_task(background_thread)
    socketio.start_background_task(timer_thread)
    socketio.start_background_task(volunteer_thread)
    socketio.run(app, port=4444)
