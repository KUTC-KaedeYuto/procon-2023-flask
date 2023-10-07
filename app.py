from flask import *
import requests
from controller import *

app = Flask(__name__)
home_url = 'http://localhost:3000/'
controller = None


def get(url: str, token: str):
    header = {
        'procon-token': token
    }
    res = requests.get(home_url + url, headers=header)
    print(res.status_code)
    return res

@app.route("/")
def get_page():
    return render_template('index.html')

@app.route("/matches")
def get_match_list():
    global controller
    token = request.args.get('procon-token')
    res = get('matches', token)
    if res.status_code == 200 and not controller:
        controller = GameController(res.json(), token, get)
    return res.text, res.status_code

@app.route("/match")
def get_match_info():
    match_id = request.args.get('match_id')
    if controller and not controller.initialized:
        controller.selectMatch(int(match_id))
        controller.start()
        return controller.getBoard()
    
    return "Failed to initialize GameController", 500



app.run(debug=True, port=5000, host='0.0.0.0')