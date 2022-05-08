import json
from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)

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
    global command, status, errorMessage
    if(command == ""):
        command = "ledSwitch"
        status = "Promena stanja diode u toku"
        errorMessage = ""
    else:
        errorMessage = "Već je poslat neki zahtev. Nemoguće je poslati drugi zahtev."
    return render_template("dashboard.html", status=status, errorMessage=errorMessage)

@app.route('/changeVentialtionSpeed/<speed>', methods=['GET'])
def changeVentialtionSpeed(speed):
    global command, status, errorMessage
    if(command == ""):
        command = "*changeVentialtionSpeed:" + speed + ";"
        status = "Promena brzine ventilatora na " + speed + " u toku"
        errorMessage = ""
    else:
        errorMessage = "Već je poslat neki zahtev. Nemoguće je poslati drugi zahtev."
    return render_template("dashboard.html", status=status, errorMessage=errorMessage)

@app.route('/openCloseDoors', methods=['GET'])
def openCloseDoors():
    global command, status, errorMessage
    if(command == ""):
        command = "openCloseDoors" 
        status = "Otvaranje/zatvaranje vrata u toku"
        errorMessage = ""
    else:
        errorMessage = "Već je poslat neki zahtev. Nemoguće je poslati drugi zahtev."
    return render_template("dashboard.html", status=status, errorMessage=errorMessage)

if __name__ == "__main__":
    app.run(port=5000, debug=True)