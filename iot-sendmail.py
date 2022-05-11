import requests
from flask import Flask
from datetime import datetime, timedelta
from flask_mail import Mail, Message
#from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'castleville.crowns@gmail.com'
app.config['MAIL_PASSWORD'] = "ebnh gwbg vurt elun"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

@app.after_server_start
def sendMail():
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

    return "MAIL SENT", 200

if __name__ == "__main__":
    #mailSendingBackgroundScheduler = BackgroundScheduler()
    #mailSendingBackgroundScheduler.add_job(sendMail, 'interval', hours=24)
    #mailSendingBackgroundScheduler.start()
    app.run(port=5000, debug=True)
    requests.get("/")