from flask import Flask, jsonify, request, render_template
import urllib.request
import urllib.error

# Iniciar la aplicación Flask.
app = Flask(__name__)

# Direcciones de los actores con contacto.
registro_url = "http://registro:5004"


class Servicio:
    def __init__(self):
        # Variables para la monitorización.
        self.did_con_acceso = None

    def realizar_peticion(self, url_completa, datos_bytes, metodo):
        return urllib.request.Request(
            url=url_completa,
            headers={'Content-Type': 'application/json'},
            data=datos_bytes,
            method=metodo,
        )


@app.route('/', methods=['GET'])  # http://127.0.0.1:5005
def inicio():
    return render_template('servicio.html', servicio=servicio)


######################
# Prueba de Concepto A
######################

@app.route('/nuevo_actor', methods=['POST'])  # Paso 3.
def nuevo_actor():
    # Leer los datos recibidos.
    datos = request.get_json()
    titular_did = datos['did']

    # Añadir el DID como actor con acceso.
    servicio.did_con_acceso = titular_did
    return jsonify({"Respuesta": "El nuevo actor **SI** ha sido incluido en el sistema."}), 200


######################
# Prueba de Concepto B
######################

@app.route('/comprobar_token', methods=['POST'])  # Paso 3.
def comprobar_token():
    # Leer los datos recibidos.
    datos = request.get_json()
    titular_did = datos['did']
    # Redirigir la petición a otro endpoint.
    peticion = servicio.realizar_peticion(registro_url + '/comprobar_token', request.get_data(), 'POST')

    try:
        # Comprobar el código de la respuesta.
        respuesta = urllib.request.urlopen(peticion)
        codigo_estado = respuesta.getcode()

        if codigo_estado == 200:
            # Añadir el DID como actor con acceso.
            servicio.did_con_acceso = titular_did

            # Comunicar la resolución definitiva.
            return jsonify({"Respuesta": "El token de acceso **SI** es valido."}), 200
    except urllib.error.HTTPError:
        return jsonify({"Respuesta": "El token de acceso **NO** es valido."}), 400


if __name__ == "__main__":
    servicio = Servicio()
    app.run(host='0.0.0.0', port=5005)
