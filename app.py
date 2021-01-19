# Flask barebones
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('index.html', title='submit')

@app.route('/student.html', methods=["POST", "GET"])
def student():
    # If POST methods
    if request.method == "POST":
        
        # Get mood from the form
        mood = request.form['mood']

        # Get elaborate stats
        elaborate = request.form['elaborate']

        # Get desc
        desc = request.form['desc'] # This doesn work

        # Let see what it will print
        print(mood,elaborate,desc)

        return render_template('student.html', title='student')
    
    if request.method == "GET":
        return render_template('student.html', title='student')

@app.route('/professor.html', methods=["POST", "GET"])
def instructor():
    return render_template('professor.html', title='instructor')


if __name__ == '__main__':
    app.run(debug=True)
