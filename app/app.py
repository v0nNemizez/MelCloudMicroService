from melcloud import MelcloudController
from flask import Flask, request, jsonify
from prometheus_client import Counter
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
import json

def open_config():
    with open('./config.json', 'r') as f:
        data = json.loads(f.read())

    return data

username = open_config()['username']
password = open_config()['password']

get_request = Counter('melflask_get_requests','Counts GET-requests')
post_request = Counter('melflask_post_requests', 'Counts POST-requests')
login_requests = Counter('melflask_login_requests', 'login requests via flaskapp')

heat = MelcloudController(username, password)

app = Flask(__name__)

@app.route("/powerstatus", methods=['GET'])
def power_status():
    if (request.method == 'GET'):
        power_status = heat.has_power
        data = {"power_on": power_status}
        get_request.inc(1)
        return jsonify(data)

@app.route("/settemp", methods=['GET','POST'])
def set_temp():
    content_type = request.content_type
    if(request.method == 'POST'):
        if content_type == 'application/json':
            temperature = request.json['temperature']
            json_response = heat.set_temperature(temperature)
            post_request.inc(1)
            return jsonify(json_response)

    elif(request.method == 'GET'):
        set_temprature = heat.settemprature
        j = {'SetTemperature': set_temprature}
        get_request.inc(1)
        return jsonify(j)

@app.route("/setfanspeed", methods=['GET','POST'])
def set_fanspeed():
    content_type = request.content_type
    if(request.method == 'POST'):
        if content_type == 'application/json':
            fanspeed = request.json['fanspeed']
            json_response = heat.set_fan_speed(fanspeed)
            post_request.inc(1)
            return jsonify(json_response)

    elif(request.method == 'GET'):
        setfanspeed = heat.fanspeed
        j = {'SetFanSpeed': setfanspeed}
        get_request.inc(1)
        return jsonify(j)

@app.route("/setoperationmode", methods=['GET','POST'])
def set_operationmode():
    content_type = request.content_type
    if(request.method == 'POST'):
        if content_type == 'application/json':
            set_operationmode = request.json['operation_mode']
            json_response = heat.set_operation_mode(set_operationmode)
            post_request.inc(1)
            return jsonify(json_response)

    elif(request.method == 'GET'):
        operationmode = heat.operation_mode
        j = {'SetFanSpeed': operationmode}
        get_request.inc(1)
        return jsonify(j)

@app.route("/update", methods=['GET'])
def update():
        get_request.inc(1)
        if heat.update_device_data() is True:
            return {"update_result":"sucsess"}
        else:
            return {"update_result": "failed"}

@app.route("/login", methods=['GET'])
def login():
    get_request.inc(1)
    login_requests.inc(1)
    if heat.login() is True:
        return {"login_result":"success"}
    else:
        return {"login_result": "failed"}



app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__=='__main__':
    app.run(debug=True)