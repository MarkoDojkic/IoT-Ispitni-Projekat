import requests
import json
import threading
import time
from flask import Flask, render_template
from turbo_flask import Turbo
from flask_cors import CORS


app = Flask(__name__)
turbo = Turbo(app)

CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

command=""
status=""
errorMessage=""
relayStatus_display = ""
doorStatus_display = ""
ventilation_display = ""
illuminationLux_display = ""
illuminationPercentage_display  = ""
tempCelsius_display = ""

@app.before_first_request
def before_first_request():
    threading.Thread(target=updateFrontend).start()

def updateFrontend():
    with app.app_context():
        while True:
            time.sleep(5)
            turbo.push(turbo.replace(render_template("dynamicData.html", status=status, errorMessage=errorMessage, relayStatus_display = relayStatus_display, doorStatus_display = doorStatus_display, ventilation_display = ventilation_display, illuminationLux_display = illuminationLux_display, illuminationPercentage_display = illuminationPercentage_display, tempCelsius_display = tempCelsius_display),"turboFlaskTarget"))

@app.route('/')
def dashboard():
    global status, errorMessage
    return render_template("dashboard.html")

@app.route('/getCommand', methods=['GET'])
def getCommand():
    global command

    app.response_class(
        response=json.dumps(command),
        status=200,
        mimetype='application/json'
    )

    return command, 200

@app.route('/clearCommand', methods=['GET'])
def clearCommand():
    global command
    command = ""
    return '', 200

@app.route('/changeRelay', methods=['GET'])
def changeDiode():
    global command, status, errorMessage
    if(command == ""):
        command = "|relaySwitch|"
        status = "Promena stanja releja diode/svetla u toku!"
        errorMessage = ""
    else:
        errorMessage = "Već je poslat neki zahtev. Nemoguće je poslati drugi zahtev!"
    return '', 200

@app.route('/changeVentilationSpeed/<speed>', methods=['GET'])
def changeVentialtionSpeed(speed):
    global command, status, errorMessage
    if(command == ""):
        command = "|$changeVentilationSpeed$" + speed + "$|"
        status = "Promena brzine ventilatora na " + speed + " u toku!"
        errorMessage = ""
    else:
        errorMessage = "Već je poslat neki zahtev. Nemoguće je poslati drugi zahtev!"
    return '', 200

@app.route('/openCloseDoors', methods=['GET'])
def openCloseDoors():
    global command, status, errorMessage
    if(command == ""):
        command = "|openCloseDoors|" 
        status = "Otvaranje" if relayStatus_display != "1" else "Zatvaranje" + " vrata u toku!"
        errorMessage = ""
    else:
        errorMessage = "Već je poslat neki zahtev. Nemoguće je poslati drugi zahtev!"
    return '', 200

@app.route('/arduino/relayState/<relayState>', methods=['GET'])
def updateRelayState(relayState):
    global relayStatus_display
    relayStatus_display = relayState
    requests.get("https://api.thingspeak.com/update?api_key=78YAN1V93W693DPA&field1=" + relayState)
    return '', 200

@app.route('/arduino/doorState/<doorState>', methods=['GET'])
def updateDoorState(doorState):
    global doorStatus_display
    doorStatus_display = str(doorState)
    requests.get("https://api.thingspeak.com/update?api_key=78YAN1V93W693DPA&field3=" + doorState)
    return '', 200

@app.route('/uTS/<ventilation>/<illuminationLux>/<illuminationPercentage>/<tempCelsius>', methods=['GET'])
def updateReadings(ventilation,illuminationLux,illuminationPercentage,tempCelsius):
    global ventilation_display, illuminationLux_display, illuminationPercentage_display, tempCelsius_display
    ventilation_display = ventilation + " RPM"
    illuminationLux_display = illuminationLux + " LUX"
    illuminationPercentage_display = illuminationPercentage + "%"
    tempCelsius_display = tempCelsius + "°C"
    requests.get("https://api.thingspeak.com/update?api_key=78YAN1V93W693DPA&field2=" + ventilation + "&field4=" + illuminationLux + "&field5=" + illuminationPercentage + "&field6=" + tempCelsius)
    return '', 200

if __name__ == "__main__":
    app.run(port=21682, debug=True)