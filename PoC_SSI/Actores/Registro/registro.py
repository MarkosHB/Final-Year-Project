from flask import Flask, jsonify, request, render_template
from datetime import datetime, timedelta
import urllib.request
import urllib.error
import didkit
import json
import jwt

# Iniciar la aplicación Flask.
app = Flask(__name__)

# Direcciones de los actores con contacto.
verificador_url = "http://verificador:5003"
servicio_url = "http://servicio:5005"


class Registro:
    def __init__(self):
        self.key = didkit.generate_ed25519_key()
        self.archivo = dict()  # DID --> Hash credencial

        # Variables para la monitorización.
        self.credencial = None

    def crear_token(self, titular_did):
        payload = {
            "usuario": titular_did,
            'validFrom': datetime.now().isoformat(),
            "validUntil": (datetime.now() + timedelta(hours=1)).isoformat(),
        }
        token = jwt.encode(payload, self.key, algorithm='HS256')
        self.archivo[titular_did] = token
        return token

    def comprobar_token(self, titular_did, titular_token):
        # El DID debe estar registrado.
        if titular_did not in self.archivo:
            return False

        # Han de coincidir ambos, el token almacenado y el proporcionado.
        token_valido = self.archivo[titular_did] == titular_token
        # Ha de estar vigente según el token generado a partir de la credencial.
        token_descodificado = jwt.decode(self.archivo[titular_did], self.key, algorithms='HS256')
        fecha_valida = datetime.fromisoformat(token_descodificado["validUntil"]) > datetime.now()

        # Ambas condiciones deben darse.
        return token_valido and fecha_valida

    def realizar_peticion(self, url_completa, datos_bytes, metodo):
        return urllib.request.Request(
            url=url_completa,
            headers={'Content-Type': 'application/json'},
            data=datos_bytes,
            method=metodo,
        )


@app.route('/', methods=['GET'])  # http://127.0.0.1:5004
def inicio():
    return render_template('registro.html', registro=registro)


###################################################
# Endpoints compartidos por las Pruebas de Concepto
###################################################

@app.route('/gestionar_acceso', methods=['POST'])  # Paso 2.
def gestionar_acceso():
    # Leer los datos recibidos.
    datos = request.get_json()
    titular_credencial = datos['credencial']

    # Verificar que se adjunta una credencial.
    if titular_credencial is None:
        return jsonify({"Respuesta": "La credencial **NO** ha sido incluida en la peticion."}), 400

    # Redirigir la petición a otro endpoint.
    datos_bytes = json.dumps(titular_credencial).encode('utf-8')
    peticion = registro.realizar_peticion(verificador_url + '/comprobar_identidad', datos_bytes, 'POST')

    try:
        # Obtener el código de la respuesta.
        respuesta = urllib.request.urlopen(peticion)
        codigo_estado = respuesta.getcode()

        if codigo_estado == 200:
            # Realizar las acciones pertinentes.
            titular_did = str(titular_credencial["credentialSubject"]['id'])
            token = registro.crear_token(titular_did)
            registro.credencial = titular_credencial

            # Comunicar la resolución definitiva.
            return jsonify({"token": token}), 200
    except urllib.error.HTTPError as e:
        if e.getcode() == 401:
            return jsonify({"Respuesta": "La identificacion **NO** ha sido exitosa."}), 401
        else:
            return jsonify({"Respuesta": "La identificacion **NO** se ha podido efectuar."}), 400


@app.route('/comprobar_token', methods=['POST'])  # Paso 3.
def comprobar_token():
    # Leer los datos recibidos.
    datos = request.get_json()
    titular_did = datos['did']
    titular_token = datos['token_acceso']

    # Realizar las acciones pertinentes.
    check = registro.comprobar_token(titular_did, titular_token)

    if check:
        # Redirigir la petición a otro endpoint.
        datos_raw = {'did': titular_did}
        datos_bytes = json.dumps(datos_raw).encode('utf-8')
        peticion = registro.realizar_peticion(servicio_url + '/nuevo_actor', datos_bytes, 'POST')

        # Obtener el código de la respuesta.
        respuesta = urllib.request.urlopen(peticion)
        codigo_estado = respuesta.getcode()

        if codigo_estado == 200:
            # Comunicar la resolución definitiva.
            return jsonify({"Respuesta": "El Titular **SI** tiene autorizacion para acceder al Servicio."}), 200
    else:
        return jsonify({"Respuesta": "El Titular **NO** tiene autorizacion para acceder al Servicio."}), 400


if __name__ == "__main__":
    registro = Registro()
    app.run(host='0.0.0.0', port=5004)
