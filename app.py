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
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        country = request.form.get("country")

        if not name:
            return render_template("register.html", error="Introduce tu nombre")
        elif not email:
            return render_template("register.html", error="Introduce tu correo electronico")
        elif not country:
            return render_template("register.html", error="Introduce tu pais")
        elif confirmation != password or not password or not confirmation:
            return render_template("register.html", error="Coloca una contraseña valida")
        password = generate_password_hash(password)

        try:
            con = sqlite3.connect('edad-de-oro.db')
            cur = con.cursor()

            try:
                cur.execute('INSERT INTO users(name, email, hash, country) VALUES (?, ?, ?, ?);', (name, email, password, country))

            
            
            except Exception as e:
                print(f"Error en la edicion de la base de datos: {str(e)}")
            
            finally:
                cur.close()
        
        except Exception as e:
            print(f"Error en creacion de conexion y cursor: {str(e)}")
        finally:
            con.commit()
            con.close()
            
        return redirect('/login')
    else:
        return render_template("register.html")
    
if __name__ == '__main__':
    app.run()