from flask import *
import requests
import logging
from controller import GameController
from typing import *
from utils import OriginalJSONProvider

Flask.json_provider_class = OriginalJSONProvider
app = Flask(__name__)
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
    print(res.status_code)
    return res

@app.route("/")
def get_page():
    return render_template('index.html')

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

@app.route("/test")
def test_method():
    for i in range(4, 7):
        controller.allocate({
            'mason_id': 1,
            'action_type': 'build',
            'action_data': {
                'x': i,
                'y': 3
            }
        })
        controller.allocate({
            'mason_id': 2,
            'action_type': 'build',
            'action_data': {
                'x': i,
                'y': 7
            }
        })
    for i in range(4, 7):
        controller.allocate({
            'mason_id': 1,
            'action_type': 'build',
            'action_data': {
                'x': 7,
                'y': i
            }
        })
        controller.allocate({
            'mason_id': 2,
            'action_type': 'build',
            'action_data': {
                'x': 3,
                'y': i
            }
        })

    return "success"

@app.route("/test1")
def test_method1():
    for i in range(4, 7):
        controller.allocate({
            'mason_id': 1,
            'action_type': 'destroy',
            'action_data': {
                'x': i,
                'y': 3
            }
        })
        controller.allocate({
            'mason_id': 2,
            'action_type': 'destroy',
            'action_data': {
                'x': i,
                'y': 7
            }
        })
    for i in range(4, 7):
        controller.allocate({
            'mason_id': 1,
            'action_type': 'destroy',
            'action_data': {
                'x': 7,
                'y': i
            }
        })
        controller.allocate({
            'mason_id': 2,
            'action_type': 'destroy',
            'action_data': {
                'x': 3,
                'y': i
            }
        })

    return "success"

@app.route("/test2")
def test_method2():
    for m in controller.mason_list:
        m.allocateAutoAction()
    return 'success'

app.run(debug=True, port=5000, host='0.0.0.0')