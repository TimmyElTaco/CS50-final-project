from flask import render_template, request, Flask, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session

import sqlite3

#configuration of application
app = Flask(__name__)

#configuration of session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        return redirect('/')
    else:
        return render_template("login.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        return redirect('/')
    else:
        return render_template("register.html")