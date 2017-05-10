from flask import Flask
app = Flask(__name__)

@app.route('/')
def madpy_habits():
    return 'Welcome to Madpy!'
