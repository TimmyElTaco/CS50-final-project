from flask import render_template, request, Flask, session, redirect, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session
from datetime import date, datetime

import requests
import random
import sqlite3

#configuration of application
app = Flask(__name__)


#configuration of session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

imageStockHealth = [
        "../static/img/image-stock-health1.jpg",
        "../static/img/image-stock-health2.jpg",
        "../static/img/image-stock-health3.jpg",
        "../static/img/image-stock-health4.jpg",
        "../static/img/image-stock-health5.jpg",
        "../static/img/image-stock-health6.jpg"
    ]


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        reminder = request.form.get('reminder')
        date_user_str = request.form.get('date')
        
        date_now = date.today()
        date_user = datetime.strptime(date_user_str, '%Y-%m-%d').date()        
        
        if date_now >= date_user:
            return render_template("index.html", error="Tienes que ingresar una fecha futura")
        if not reminder:
            return render_template("index.html", error="Ingresa tu recordatorio.")
        if not date_user_str:
            return render_template("index.html", error="Ingresa una fecha.")
        if len(reminder) > 300: 
            return render_template("index.html", error="Numero de caracteres maximo es de 300.")
        print(f"{session["user_id"]}")
        try: 
            con = sqlite3.connect('edad-de-oro.db')
            cur = con.cursor()

            try:
                cur.execute('INSERT INTO reminders (user_id, reminder, date_reminder) VALUES (?, ?, ?);', (session["user_id"], reminder, date_user))

            except Exception as e:
                print(f"Error al modificar la base de datos: {str(e)}")

            finally:
                cur.close()

        except Exception as e:
            print(f"Error al conectar con la base de datos: {str(e)}")
        
        finally:
            con.commit()
            con.close()

        return redirect('/')

    else: 
        if not session:
            return redirect('/login')

        news = call_api()

        arrNews = []
        for n in range(0, 4):
            arrNews.append({})
            arrNews[n]["title"] = news["articles"][n]["title"]
            arrNews[n]["url"] = news["articles"][n]["url"]

            if news["articles"][n]["urlToImage"] == None:
                arrNews[n]["img"] = imageStockHealth[random.randint(0, 5)]
            else:
                arrNews[n]["img"] = news["articles"][n]["urlToImage"]
            
            if news["articles"][n]["description"] == None:
                arrNews[n]["description"] = ""
            else:
                arrNews[n]["description"] = news["articles"][n]["description"]

        try:
            con = sqlite3.connect('edad-de-oro.db')
            cur = con.cursor()

            try: 
                cur.execute('SELECT user_id, reminder, date_reminder FROM reminders;')
                reminders = cur.fetchall()
                print(f"{reminders}")

            except Exception as e:
                print(f"Error al consultar la base de datos: {str(e)}")
            
            finally:
                cur.close()

        except Exception as e:
            print(f"Error al crear el cursor: {str(e)}")

        finally:
            con.commit()
            con.close()

        print(f"{reminders}")

        return render_template("index.html", news=arrNews, reminders=reminders)
    

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
                session["user_id"] = user[0][0]

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
    

@app.route('/noticias')
def news():
    news = call_api()

    arrNews = []
    for n in range(0, 20):
        arrNews.append({})
        arrNews[n]["title"] = news["articles"][n]["title"]
        arrNews[n]["url"] = news["articles"][n]["url"]

        if news["articles"][n]["urlToImage"] == None:
            arrNews[n]["img"] = imageStockHealth[random.randint(0, 5)]
        else:
            arrNews[n]["img"] = news["articles"][n]["urlToImage"]
        if news["articles"][n]["description"] == None:
            arrNews[n]["description"] = "Este articulo no cuenta con una descripcion."
        else:
            arrNews[n]["description"] = news["articles"][n]["description"]
        
        arrNews[n]["author"] = news["articles"][n]["author"]

    return render_template("news.html", news=arrNews)


@app.route('/logout')
def logout():
    session.clear()

    return redirect('/login') 


def call_api():
    try:
        url = ('https://newsapi.org/v2/top-headlines?'
            'category=health&'
            'country=mx&'
            'apiKey=c334ef5152a44a348d7e12163028dbc3')

        response = requests.get(url)
        data = response.json()
        return data

    except Exception as e:
        print(f"Error al llamar al API: {str(e)}")

        
if __name__ == '__main__':
    app.run()