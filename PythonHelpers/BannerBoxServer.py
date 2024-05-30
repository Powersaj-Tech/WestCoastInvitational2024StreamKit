from flask import Flask
from flask_cors import CORS

# pip install flask-cors
# pip install Flask

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

currentmsg = "Default Server Message"

@app.route('/GetActiveMessage')
def get_data():
    return currentmsg

@app.route('/UpdateMessageCall/<data>')
def post_data(data):
    global currentmsg
    currentmsg = data
    return f"Received message: {data}"

if __name__ == '__main__':
    app.run(port=44444, debug=False)