from flask import Flask, jsonify
from flask_cors import CORS
import threading
import webbrowser
import mysql.connector

app = Flask(__name__)
CORS(app)

config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'cinestar'
}

configRemote = {
    'host': 'srv1101.hstgr.io',
    'user': 'u584908256_cinestar',
    'password': 'Senati2023@',
    'database': 'u584908256_cinestar'
}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor(dictionary=True)


@app.route('/cines')
def cines():
    cursor.callproc('sp_getCines')
    for data in cursor.stored_results():
        cines = data.fetchall()

    return jsonify(cines)


@app.route('/cine/<int:id>')
def cine(id):
    cursor.callproc('sp_getCine', (id,))
    for data in cursor.stored_results():
        cine = data.fetchone()

    cursor.callproc('sp_getCinePeliculas', (id,))
    for data in cursor.stored_results():
        peliculas = data.fetchall()

    cursor.callproc('sp_getCineTarifas', (id,))
    for data in cursor.stored_results():
        tarifas = data.fetchall()

    cine['peliculas'] = peliculas
    cine['tarifas'] = tarifas
    return jsonify(cine)


@app.route('/peliculas/<id>')
def peliculas(id):
    id = 1 if id == 'cartelera' else 2 if id == 'estrenos' else 0

    if id == 0:
        return jsonify([])

    cursor.callproc('sp_getPeliculas', (id,))
    for data in cursor.stored_results():
        peliculas = data.fetchall()
        return jsonify(peliculas)


@app.route('/pelicula/<int:id>')
def pelicula(id):
    cursor.callproc('sp_getPelicula', (id,))
    for data in cursor.stored_results():
        pelicula = data.fetchone()

    return jsonify(pelicula)


def open_browser():
    # Abrir el navegador con la página principal de la API
    webbrowser.open_new_tab("http://127.0.0.1:5000/cines")


if __name__ == "__main__":
    # Iniciar el servidor Flask en un hilo separado
    threading.Thread(target=app.run).start()
    
     
    import time
    time.sleep(2)
    
    # Abrir el navegador en otro hilo
    threading.Thread(target=open_browser).start()