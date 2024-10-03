from flask import Flask, jsonify, request, render_template
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import hashlib
import json


# Iniciar la aplicacion Flask.
app = Flask(__name__)

# Direcciones de los actores con contacto.
blockchain_url = 'http://nodo_principal:8545'


class Verificador:
    def __init__(self):
        self.cuenta = "0xf17f52151EbEF6C7334FAD080c5704D77216b732"
        self.priv_key = "ae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f"

        # Variables para la monitorización.
        self.dir_contrato = None
        self.credencial = None
        self.hash_blockchain = None
        self.hash_credencial = None

    def identificar_titular(self, w3, titular_credencial, titular_did):
        # Obtener el abi desde el fichero local.
        with open('contrato.abi', 'r') as abi_file:
            abi = json.load(abi_file)

        # Creación de la instancia del contrato.
        contrato_credenciales = w3.eth.contract(address=self.dir_contrato, abi=abi)

        # Llamar a la función del contrato que obtiene el hash de la credencial almacenada.
        self.hash_blockchain = contrato_credenciales.functions.obtenerHashCredencial(titular_did).call()
        # Generar el hash de la credencial recibida.
        self.hash_credencial = hashlib.sha256(json.dumps(titular_credencial, sort_keys=True).encode('utf-8')).digest()

        return self.hash_blockchain == self.hash_credencial


@app.route('/', methods=['GET'])  # http://127.0.0.1:5003
def inicio():
    return render_template('verificador.html', verificador=verificador)


###################################################
# Endpoints compartidos por las Pruebas de Concepto
###################################################

@app.route('/recibir_direccion_contrato', methods=['POST'])  # Paso 1.
def recibir_direccion_contrato():
    # Obtener los datos de la petición.
    datos = request.get_json()
    verificador.dir_contrato = str(datos['dir_contrato'])

    # Comunicar la resolución definitiva.
    return jsonify({"Respuesta": "La direccion del contrato **SI** ha sido recibido."}), 200


@app.route('/comprobar_identidad', methods=['POST'])  # Paso 2.
def comprobar_identidad():
    # Establecer la conexión con la blockchain.
    w3 = Web3(Web3.HTTPProvider(blockchain_url))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    # Comprobar que la blockchain está operativa.
    if w3.is_connected():
        # Obtener los datos de la petición.
        titular_credencial = request.get_json()
        verificador.credencial = titular_credencial
        titular_did = str(titular_credencial["credentialSubject"]["id"])

        # Realizar las acciones pertinentes.
        check = verificador.identificar_titular(w3, titular_credencial, titular_did)

        # Comunicar la resolución definitiva.
        if check:
            return jsonify({"Respuesta": "El Titular **ES** quien dice ser."}), 200
        else:
            return jsonify({"Respuesta": "El Titular **NO** es quien dice ser."}), 401
    else:
        return jsonify({"Respuesta": "La conexion a la Blockchain **NO** pudo efectuarse."}), 400


if __name__ == "__main__":
    verificador = Verificador()
    app.run(host='0.0.0.0', port=5003)
