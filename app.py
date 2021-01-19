# Flask barebones
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('submit.html', title='submit')

@app.route('/student', methods=["POST", "GET"])
def student():
    return render_template('studentPortal.html', title='student')

@app.route('/instructor', methods=["POST", "GET"])
def instructor():
    return render_template('instructorPortal.html', title='instructor')


if __name__ == '__main__':
    app.run(debug=True)
