import time
from flask import Flask
from flask import request, redirect, url_for, render_template
import interact
import json

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('home.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        out = {"values": {}}
        for key in request.form:
            out['values'][key] = {
                'value': request.form[key] * 1
            }

        interact.set(out)

        return redirect(url_for('get'))

    return redirect(url_for('hello'))


@app.route('/get')
def get():
    data = interact.read()
    return render_template('get.html', dat = json.dumps(data))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
