import imp
import json
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
#import serial
from threading import Thread
import time

#PORT = "COM12"
#BAUD_RATE = 9600


objectDic = {}

#objectDic[14] = {"sensor" : "potenciometar", "value": 0, "lastUpdate": "00:00:00"}
#objectDic[2] = {"sensor" : "taster", "value": 0, "lastUpdate": "00:00:00"}


running = True
#serialConnection = serial.Serial(PORT, BAUD_RATE)
"""
def receive(serialConnection):
    global running
    
    while running:
        
        if serialConnection.in_waiting > 0:
            receivedMessage = serialConnection.read_until(b';').decode('ascii')
            processMessage(receivedMessage)
        time.sleep(0.1)

def processMessage(message):
    # ODGOVOR : "ARDUINO_ID:PIN|VREDNOST;"
    
    l = message[:-1].split(":")
    arudinoId = int(l[0])
    pin = int(l[1].split("|")[0])
    val = int(l[1].split("|")[1])

    objectDic[pin]['value'] = val;
    objectDic[pin]['lastUpdate'] = time.strftime();

threadReceiver = Thread(target=receive, args=(serialConnection,))
threadReceiver.start()

app = Flask(__name__)

@app.route('/')
def dashboard():
    global objectDic
    return render_template("dashboard.html", data=objectDic)

@app.route('/on/<pin_id>', methods=['GET'])
def turnOn(pin_id):
    global serialConnection
    text = getWriteMessage(0, pin_id, 1)
    serialConnection.write(text.encode('ascii'))
    return render_template("dashboard.html")
    # return jsonify(isError=False, message="Success", statusCode=200, data=pin_id)

@app.route('/off/<pin_id>', methods=['GET'])
def turnOff(pin_id):
    global serialConnection
    text = getWriteMessage(0, pin_id, 0)
    serialConnection.write(text.encode('ascii'))
    return render_template("dashboard.html")
    # return jsonify(isError=False, message="Success", statusCode=200, data=pin_id)

@app.route('/setDigital/<pin_id>/<value>', methods=['GET'])
def setDigital(pin_id, value):
    global serialConnection
    if not (int(value) == 0):
        value = 1
    else:
        value = 0
    
    text = getWriteMessage(0, pin_id, int(value))
    serialConnection.write(text.encode('ascii'))
    return render_template("dashboard.html")

@app.route('/setAnalog/<pin_id>/<value>', methods=['GET'])
def setAnalog(pin_id, value):
    global serialConnection
    text = getWriteMessage(0, pin_id, value)
    serialConnection.write(text.encode('ascii'))
    return render_template("dashboard.html")

def getWriteMessage(controllerId, pin, value):
    return str(controllerId) + ":W:" + str(pin) + ":" + str(value) + ";"

def getReadMessage(controllerId):
    return str(controllerId) + ":R;"

"""
app = Flask(__name__)

CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

command=""

@app.route('/')
def dashboard():
    global objectDic
    return render_template("dashboard.html")

@app.route('/commandData', methods=['GET'])
def getCommand():
    global command
    app.response_class(
        response=json.dumps(command),
        status=200,
        mimetype='application/json'
    )
    return command

@app.route('/clearCommand', methods=['GET'])
def clearCommand():
    global command
    command = ""
    return

@app.route('/changeDiode', methods=['GET'])
def changeDiode():
    global command
    command = "ledSwitch"
    return render_template("dashboard.html")

@app.route('/changeVentialtionSpeed/<speed>', methods=['GET'])
def changeVentialtionSpeed(speed):
    global command
    command = "changeVentialtionSpeed:" + speed
    return render_template("dashboard.html")

@app.route('/openCloseDoors', methods=['GET'])
def openCloseDoors():
    global command
    command = "openCloseDoors"
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(port=5000, debug=True)