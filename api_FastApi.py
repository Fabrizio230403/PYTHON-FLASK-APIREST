import subprocess # Importar el módulo subprocess para ejecutar comandos
import webbrowser # Importar el módulo webbrowser para abrir páginas web
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException # Importar FastAPI y HTTPException de FastAPI para construir la API
from fastapi.middleware.cors import CORSMiddleware # Importar CORSMiddleware de FastAPI para configurar CORS
from typing import List, Dict, Any # Importa List, Dict y Any de typing para definir tipos de datos
import mysql.connector

app = FastAPI(debug=False) # Crear una instancia de FastAPI y desactivar el modo debug
 
# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir acceso desde cualquier origen
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Configuración de la conexión a la base de datos
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'cinestar'
}

configRemote = {
    'host' : 'srv1101.hstgr.io',
    'user' : 'u584908256_cinestar',
    'password' : 'Senati2823@',
    'database' : 'cinestar'
}

# Función auxiliar para ejecutar procedimientos almacenados
def call_stored_procedure(procedure_name: str, *args: Any) -> List[Dict[str, Any]]:
    with mysql.connector.connect(**config) as cnx: #Conectar a mi base de datos
        with cnx.cursor(dictionary=True) as cursor: #Crear un cursor para consultas SQL
            cursor.callproc(procedure_name, args) #Ejecutar el procedimiento almacenado
            for data in cursor.stored_results(): #Iterar sobre los resultados de mi procedimiento
                return data.fetchall() #Devuelve los resultados como una lista de diccionarios

index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API FastAPI</title>
    <style>
        button {
            font-size: 20px;  /* Tamaño de letra de los botones */
            padding: 10px 20px;  /* Espaciado dentro de los botones */
            margin: 5px;  /* Espaciado entre los botones */
        }
    </style>
</head>
<body>
    <h1>API FastAPI</h1>
    <button onclick="openDocs()">Documentación</button>
    <button onclick="openCines()">Cines</button>
    <button onclick="openCine()">Cine Específico</button>
    <button onclick="openCartelera()">Cartelera</button>
    <button onclick="openEstrenos()">Estrenos</button>
    <button onclick="openPelicula()">Película Específica</button>

    <script>
        function openDocs() {
            window.open("http://localhost:8000/docs", "_blank");
        }
        function openCines() {
            window.open("http://localhost:8000/cines", "_blank");
        }
        function openCine() {
            window.open("http://localhost:8000/cine/1", "_blank");
        }
        function openCartelera() {
            window.open("http://localhost:8000/peliculas/cartelera", "_blank");
        }
        function openEstrenos() {
            window.open("http://localhost:8000/peliculas/estrenos", "_blank");
        }
        function openPelicula() {
            window.open("http://localhost:8000/pelicula/1", "_blank");
        }
    </script>
</body>
</html>
"""

 # Definimos una ruta raiz , que va a responder solicitudes GET y devuelve respuesta HTML

@app.get("/", response_class=HTMLResponse)
async def index():
    return index_html # Retornar el contenido HTML almacenado en la variable index_html que se encuentra mas arriba

# Ruta de cines
@app.get('/cines')
def get_cines() -> List[Dict[str, Any]]:
    cines = call_stored_procedure('sp_getCines')
    return cines

# Ruta para obtener un cine especifico
@app.get('/cine/{id}')
def get_cine(id: int) -> Dict[str, Any]:
    cine_results = call_stored_procedure('sp_getCine', id)
    if not cine_results:
        raise HTTPException(status_code=404, detail="Cine no encontrado")
    
    cine = cine_results[0]  # Acceder al primer elemento de la lista
    
    peliculas = call_stored_procedure('sp_getCinePeliculas', id)
    tarifas = call_stored_procedure('sp_getCineTarifas', id)
    cine['peliculas'] = peliculas
    cine['tarifas'] = tarifas
    return cine

# Ruta para obtener todas las películas o filtrar por tipo (cartelera o estrenos) -> Por ejemplo: http://localhost:8000/peliculas/cartelera
@app.get('/peliculas/{id}')
def get_peliculas(id: str) -> List[Dict[str, Any]]:
    id = 1 if id == 'cartelera' else 2 if id == 'estrenos' else 0
    if id == 0:
        raise HTTPException(status_code=400, detail="Tipo de película no válido")
    peliculas = call_stored_procedure('sp_getPeliculas', id)
    return peliculas

# Ruta para obtener una película especifica
@app.get('/pelicula/{id}')
def get_pelicula(id: int) -> List[Any]:
    pelicula_data = call_stored_procedure('sp_getPelicula', id)
    if not pelicula_data:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    return pelicula_data


# Abrir automáticamente la página web al ejecutar la aplicación con uvicorn reload
if __name__ == "__main__":
    subprocess.Popen(["uvicorn", "api_FastApi:app", "--reload"]) # Ejecutar uvicorn para iniciar el servidor web con FastAPI
    webbrowser.open_new_tab("http://localhost:8000/") # Abre la página principal de la API en una pestaña


    
# Tambien, algo importante que recalcar es que FastAPI te crea ya la documentacion.