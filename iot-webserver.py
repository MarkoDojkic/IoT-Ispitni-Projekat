import json
from flask import Flask, render_template
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
#Mail config

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'castleville.crowns@gmail.com'
app.config['MAIL_PASSWORD'] = "ebnh gwbg vurt elun"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

command=""
status=""
errorMessage=""

@app.route('/')
def dashboard():
    global status, errorMessage
    return render_template("dashboard.html", status=status, errorMessage=errorMessage)

@app.route('/getCommand', methods=['GET'])
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
    return '', 200

@app.route('/changeRelay', methods=['GET'])
def changeDiode():
    global command, status, errorMessage
    if(command == ""):
        command = "relaySwitch"
        status = "Promena stanja releja diode/svetla u toku!"
        errorMessage = ""
    else:
        errorMessage = "Već je poslat neki zahtev. Nemoguće je poslati drugi zahtev!"
    return render_template("dashboard.html", status=status, errorMessage=errorMessage)

@app.route('/changeVentilationSpeed/<speed>', methods=['GET'])
def changeVentialtionSpeed(speed):
    global command, status, errorMessage
    if(command == ""):
        command = "$changeVentilationSpeed$" + speed + "$"
        status = "Promena brzine ventilatora na " + speed + " u toku!"
        errorMessage = ""
    else:
        errorMessage = "Već je poslat neki zahtev. Nemoguće je poslati drugi zahtev!"
    return render_template("dashboard.html", status=status, errorMessage=errorMessage)

@app.route('/openCloseDoors', methods=['GET'])
def openCloseDoors():
    global command, status, errorMessage
    if(command == ""):
        command = "openCloseDoors" 
        status = "Otvaranje/zatvaranje vrata u toku!"
        errorMessage = ""
    else:
        errorMessage = "Već je poslat neki zahtev. Nemoguće je poslati drugi zahtev!"
    return render_template("dashboard.html", status=status, errorMessage=errorMessage)

@app.route('/sendEmail', methods=['GET'])
def sendEmail():
    mail = Mail(app)
    subject = "Izveštaj o stanju IoT sistema - {}".format((datetime.now()- timedelta(days=1)).strftime("%d.%m.%Y"))

    thingspeakData = requests.get("https://api.thingspeak.com/channels/1726262/feeds.json?results")
    feedEntriesJSON = thingspeakData.json()["feeds"]

    temperatureValues = []
    illuminationLuxValues = []
    doorOpenedCount = 0
    relayStateChangeCount = 0
    previousRelayState = -1

    for feedEntry in feedEntriesJSON:
        if(datetime.strptime(feedEntry["created_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d") == (datetime.now()- timedelta(days=1)).strftime("%Y-%m-%d")):
            if(feedEntry["field6"] != None): temperatureValues.append(float(feedEntry["field6"]))
            if(feedEntry["field4"] != None): illuminationLuxValues.append(float(feedEntry["field4"]))
            if(feedEntry["field3"] != None and int(feedEntry["field3"]) == 1): doorOpenedCount += 1
            if(feedEntry["field1"] != None and int(feedEntry["field1"]) != previousRelayState):
                previousRelayState = int(feedEntry["field1"])
                relayStateChangeCount += 1

    body = "\
IoT izveštaj za dan {}\n\
Prosečna vrednost temperature: {} °C\n\
Prosečna osvetljenost senzora: {} Lux\n\
Ukupan broj otvaranja vrata: {}\n\
Ukupan broj promena stanja na releju diode/svetla: {}\
    ".format((datetime.now()- timedelta(days=1)).strftime("%d.%m.%Y"), 
        round(sum(temperatureValues)/len(temperatureValues), 2) if len(temperatureValues) > 0 else 0.0,
        round(sum(illuminationLuxValues)/len(illuminationLuxValues), 2) if len(temperatureValues) > 0 else 0.0,
        doorOpenedCount, relayStateChangeCount)
 
    message = Message(subject, sender = 'castleville.crowns@gmail.com', recipients = ['marko.dojkic.18@singimail.rs'])
    
    message.body = body

    mail.send(message)

@app.route('/arduino/relayState/<relayState>', methods=['GET'])
def updateRelayState(relayState):
    #change relay icon to state x
    requests.get("https://api.thingspeak.com/update?api_key=78YAN1V93W693DPA&field1=" + relayState)

@app.route('/arduino/doorUpdate/<doorUpdate>', methods=['GET'])
def updateDoorState(doorUpdate):
    #change door icon to opened/closed
    requests.get("https://api.thingspeak.com/update?api_key=78YAN1V93W693DPA&field3=" + doorUpdate)

@app.route('/arduino/updateReadings', methods=['GET'])
def updateReadings():
    #display readings
    ventilation = request.args.get('field2', default = 1, type = str)
    illuminationLux = request.args.get('field4', default = 1, type = str)
    illuminationPercentage = request.args.get('field5', default = 1, type = str)
    tempCelsius = request.args.get('field6', default = 1, type = str)
    requests.get("https://api.thingspeak.com/update?api_key=78YAN1V93W693DPA&field2=" + ventilation + "&field4=" + illuminationLux + "&field5=" + illuminationPercentage + "&field6=" + tempCelsius)

if __name__ == "__main__":
    mailSendingBackgroundScheduler = BackgroundScheduler()
    mailSendingBackgroundScheduler.add_job(sendEmail, 'interval', hours=24)
    mailSendingBackgroundScheduler.start()
    app.run(port=5000, debug=True)