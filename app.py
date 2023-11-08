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
        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            return render_template("login.html", error="Ingresa tu email")
        elif not password:
            return render_template("login.html", error="Ingresa tu contraseña")

        try:
            con = sqlite3.connect("edad-de-oro.db")
            cur = con.cursor()

            try:
                cur.execute('SELECT id, email, hash FROM users WHERE email = ?;', (email,))
                user = cur.fetchall()

                if not user:
                    return render_template("login.html", error="Email incorrecto")
                for obj in user:
                    if not check_password_hash(obj[2], password):
                        return render_template("login.html", error="Contraseña incorrecta")
                session["user_id"] = user[0]

            except Exception as e:
                print(f"Error al consultar la base de datos: {str(e)}")
            
            finally:
                cur.close()

        except Exception as e:
            print(f"Error al hacer la conexion y crear el cursor: {str(e)}")

        finally:
            con.commit()
            con.close()

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
                cur.execute('SELECT email FROM users;')
                for obj in cur.fetchall():
                    if email in obj:
                        return render_template("register.html", error="Este email ya existe")

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