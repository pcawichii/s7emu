import time
from flask import Flask
from flask import request, redirect, url_for, render_template
import interact
import json
import status.run as stat

app = Flask(__name__)

@app.route('/')
def hello():
    data = interact.read()
    return render_template('home.html', data=data)

@app.route('/novalues')
def hello_no_values():
    return render_template('home_no_values.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        out = {"values": {}}
        for key in request.form:
            if request.form[key] != "":
                out['values'][key] = {
                    'value': request.form[key] * 1
                }

        interact.set(out)

        return redirect(url_for('get'))

    return redirect(url_for('hello'))


@app.route('/get')
def get():
    data = json.dumps(interact.read(),
                                          sort_keys=False,
                                          indent=4,
                                          separators=(',', ': '))

    return render_template('get.html',
                           dat=data)


@app.route('/status')
def status():
    f = open("status/init.json")
    data = json.load(f)
    out = {}
    out['host'] = data['plc']['host']
    out['port'] = data['plc']['port']
    out['sql_host'] = data['sql']['server']

    return render_template('status_home.html', out=out)


@app.route('/status_gen')
def status_gen():
    data = stat.out()

    return render_template('status.html', dat=data)

@app.route('/selenium')
def selenium():
    print("Selenium")
    data = stat.sel()

    return render_template('selenium.html', dat=data)



if __name__ == '__main__':
    app.run(host='0.0.0.0')
