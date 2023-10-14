from flask import *
import requests
import logging
from controller import GameController
from typing import *
from utils import OriginalJSONProvider

Flask.json_provider_class = OriginalJSONProvider
app = Flask(__name__)
# home_url = 'http://172.28.0.1:8080/'
home_url = 'http://localhost:3000/'
controller: Union[GameController , None] = None

def get(url: str, token: str):
    header = {
        'procon-token': token
    }
    res = requests.get(home_url + url, headers=header)
    return res

def post(url: str, token: str, header: dict, body):
    header['procon-token'] = token
    res = requests.post(home_url + url, headers=header, data=body)
    print(res.status_code, res.content)
    return res

@app.route("/")
def get_page():
    return render_template('index.html')

@app.route("/linked")
def linked():
    return render_template('linked.html')

@app.route("/get_parent")
def get_parent_data():
    result = {
        'token': controller.token,
        'match_id': controller.match_id
    }
    return jsonify(result)

@app.route("/matches")
def get_match_list():
    global controller
    if controller:
        controller.exit()
        controller = None
    token = request.args.get('procon-token')
    res = get('matches', token)
    if res.status_code == 200 and not controller:
        controller = GameController(res.json(), token, get, post)
    return res.text, res.status_code

@app.route("/match")
def get_match_info():
    match_id = request.args.get('match_id')
    if controller:
        if not controller.initialized:
            controller.selectMatch(int(match_id))
            controller.start()
        result = controller.getInfo()
        if result:
            return jsonify(result)
        else:
            return "Too early"
    
    return "GameController is not initialized. \nPlease try again or send another request.", 500

@app.route("/allocate", methods=["POST"])
def allocate_action():
    if controller and controller.initialized:
        data = request.json
        print(data)
        res = controller.allocate(data)
        if res:
            return "success", 200
        return "Because of incorrect data, server failed to allocate action to the mason.", 400
    return "GameController is not ready.\n Please try again or send another request", 500

@app.route("/controller")
def getControllerInfo():
    if controller:
        return jsonify(controller.toDict())
    return "GameController is not instantiated.", 500

@app.route("/change", methods=["POST"])
def change_action():
    if controller and controller.initialized:
        data = request.json
        print(data)
        res = controller.change(data)
        if res:
            return "success", 200
        return "Because of incorrect data, server failed to allocate action to the mason.", 400
    return "GameController is not ready.\n Please try again or send another request", 500

app.run(debug=True, port=25566, host='0.0.0.0')