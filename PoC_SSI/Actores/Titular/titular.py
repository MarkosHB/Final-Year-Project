from flask import Flask, jsonify, render_template
import urllib.request
import urllib.error
import didkit
import json

# Iniciar la aplicación Flask.
app = Flask(__name__)

# Direcciones de los actores con contacto.
emisor_url = "http://emisor:5001"
registro_url = "http://registro:5004"
servicio_url = "http://servicio:5005"


class Titular:
    def __init__(self):
        self.key = didkit.generate_ed25519_key()
        self.did = didkit.key_to_did("key", self.key)

        # Variables para la monitorización.
        self.credencial = None
        self.token_acceso = None

    def guardar_credencial(self, credencial):
        self.credencial = json.loads(credencial)

    def guardar_token(self, token_acceso):
        self.token_acceso = token_acceso

    def realizar_peticion(self, url_completa, datos_bytes, metodo):
        return urllib.request.Request(
            url=url_completa,
            headers={'Content-Type': 'application/json'},
            data=datos_bytes,
            method=metodo,
        )


@app.route('/', methods=['GET'])  # http://127.0.0.1:5002
def inicio():
    return render_template('titular.html', titular=titular)


###################################################
# Endpoints compartidos por las Pruebas de Concepto
###################################################

@app.route('/pedir_credencial', methods=['GET'])  # Paso 1.
def pedir_credencial():
    # Construir la petición para el endpoint.
    datos_raw = {'did': titular.did}
    datos_bytes = json.dumps(datos_raw).encode('utf-8')
    peticion = titular.realizar_peticion(emisor_url + '/generar_credencial', datos_bytes, 'POST')

    try:
        # Obtener el contenido de la respuesta.
        respuesta = urllib.request.urlopen(peticion)
        credencial = str(respuesta.read().decode('utf-8'))

        # Realizar las acciones pertinentes.
        titular.guardar_credencial(credencial)

        # Comunicar la resolución definitiva.
        return jsonify({"Respuesta": "La credencial **SI** ha sido recibida y guardada."}), 200
    except urllib.error.HTTPError:
        return jsonify({"Respuesta": "La credencial **NO** ha sido recibida ni guardada."}), 400


@app.route('/obtener_acceso', methods=['GET'])  # Paso 2.
def obtener_acceso():
    # Construir la petición al endpoint.
    datos_raw = {'credencial': titular.credencial}
    datos_bytes = json.dumps(datos_raw).encode('utf-8')
    peticion = titular.realizar_peticion(registro_url + '/gestionar_acceso', datos_bytes, 'POST')

    try:
        # Obtener el código de la respuesta.
        respuesta = urllib.request.urlopen(peticion)
        codigo_estado = respuesta.getcode()

        if codigo_estado == 200:
            # Obtener el contenido de la respuesta.
            contenido = json.loads(respuesta.read().decode('utf-8'))
            token_acceso = str(contenido['token'])

            # Realizar las acciones pertinentes.
            titular.guardar_token(token_acceso)

            # Comunicar la resolución definitiva.
            return jsonify({"Respuesta": "El token de acceso **SI** ha sido recibido."}), 200
    except urllib.error.HTTPError:
        return jsonify({"Respuesta": "El token de acceso **NO** ha sido recibido."}), 400


######################################
# Endpoints de la Prueba de Concepto A
######################################

@app.route('/acceder_servicio_mediante_registro', methods=['GET'])  # Paso 3.
def acceder_servicio_mediante_registro():
    # Construir la petición al endpoint.
    datos_raw = {'token_acceso': titular.token_acceso, 'did': titular.did}
    datos_bytes = json.dumps(datos_raw).encode('utf-8')
    peticion = titular.realizar_peticion(registro_url + '/comprobar_token', datos_bytes, 'POST')

    try:
        # Comprobar el código de la respuesta.
        respuesta = urllib.request.urlopen(peticion)
        codigo_estado = respuesta.getcode()

        if codigo_estado == 200:
            # Comunicar la resolución definitiva.
            return jsonify({"Respuesta": "El acceso **SI** ha sido obtenido al servicio."}), 200
    except urllib.error.HTTPError:
        return jsonify({"Respuesta": "El acceso **NO** ha sido obtenido al servicio."}), 400


######################################
# Endpoints de la Prueba de Concepto B
######################################

@app.route('/acceder_servicio_directamente', methods=['GET'])  # Paso 3.
def acceder_servicio_directamente():
    # Construir la petición al endpoint.
    datos_raw = {'token_acceso': titular.token_acceso, 'did': titular.did}
    datos_bytes = json.dumps(datos_raw).encode('utf-8')
    peticion = titular.realizar_peticion(servicio_url + '/comprobar_token', datos_bytes, 'POST')

    try:
        # Comprobar el código de la respuesta.
        respuesta = urllib.request.urlopen(peticion)
        codigo_estado = respuesta.getcode()

        if codigo_estado == 200:
            # Comunicar la resolución definitiva.
            return jsonify({"Respuesta": "El acceso **SI** ha sido obtenido al servicio."}), 200
    except urllib.error.HTTPError:
        return jsonify({"Respuesta": "El acceso **NO** ha sido obtenido al servicio."}), 400


if __name__ == "__main__":
    titular = Titular()
    app.run(host='0.0.0.0', port=5002)
