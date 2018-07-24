from flask import Flask, render_template, redirect, url_for
import psutil
import datetime
import water_adc
import os
#import Image

app = Flask(__name__)
#url_for('static', filename='style.css')
#url_for('static', filename='lastpic.jpg')

def template(title = "Drivhuset", text = "", moisture = 0):
#    now = datetime.datetime.now()
    timeString = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    templateDate = {
        'title' : title,
        'time' : timeString,
        'text' : text
        }
    return templateDate

@app.route("/")
def hello():
    templateData = template()
    return render_template('main.html', **templateData)

@app.route("/last_watered")
def check_last_watered():
    templateData = template(text = water_adc.get_last_watered())
    return render_template('main.html', **templateData)

@app.route("/sensor")
def action():
    status = water_adc.get_moisture()
    message = ""
    if (status > 800):
        message = "Water me please! " + str(status)
    else:
        message = "I'm a happy plant " + str(status)

    templateData = template(text = message)
    return render_template('main.html', **templateData)

@app.route("/water")
def action2():
    water_adc.pump_on()
    templateData = template(text = "Watered Once")
    return render_template('main.html', **templateData)

@app.route("/auto_water/<toggle>")
def auto_water(toggle):
    running = False
    if toggle == "ON":
        templateData = template(text = "Auto Watering On")
        for process in psutil.process_iter():
            try:
                if process.cmdline()[1] == 'auto_water.py':
                    templateData = template(text = "Already running")
                    running = True
            except:
                pass
        if not running:
            os.system("python3 auto_water.py&")
    else:
        templateData = template(text = "Auto Watering Off")
        os.system("sudo pkill -f auto_water.py")
    return render_template('main.html', **templateData)

#@app.route("/show_pic")
#def vis_siste_bildet():
#    templateData = template(text = "Hentet frem siste billedet")
#    Image.open('lastpic.jpg').show()
#    return render_template('main.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)