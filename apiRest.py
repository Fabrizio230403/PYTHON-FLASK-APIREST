from flask import Flask
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

config = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : '',
    'database' : 'cinestar'
    
}

configRemote = {
    'host' : 'srv1101.hstgr.io',
    'user' : 'u584908256_cinestar',
    'password' : 'Senati2823@',
    'database' : 'cinestar'
}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor(dictionary=True)


@app.route('/cines')
def cines():
    cursor.callproc('sp_getCines')
    for data in cursor.stored_results():
        cines = data.fetchall()
    
    return cines

@app.route('/cine/<int:id>')
def cine(id):
    cursor.callproc('sp_getCine',(id,))
    for data in cursor.stored_results():
        cine = data.fetchone()
        
    cursor.callproc('sp_getCinePeliculas',(id,))
    for data in cursor.stored_results():
        peliculas = data.fetchall()
        
    cursor.callproc('sp_getCineTarifas',(id,))
    for data in cursor.stored_results():
        tarifas = data.fetchall()
     
    cine['peliculas']  = peliculas
    cine['tarifas']=tarifas
    return cine

@app.route('/peliculas/<id>')
def peliculas(id):
    id = 1 if id == 'cartelera' else 2 if id == 'estrenos' else 0
    
    if id == 0 : return
    
    cursor.callproc('sp_getPeliculas',(id,))
    for data in cursor.stored_results():
        peliculas = data.fetchall()
        return peliculas


@app.route('/pelicula/<int:id>')
def pelicula(id):
    cursor.callproc('sp_getPelicula',(id,))
    for data in cursor.stored_results():
        pelicula =  data.fetchone()
        
    return pelicula 
    
if __name__== '__main__':
    app.run()
    
