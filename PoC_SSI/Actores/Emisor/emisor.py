import urllib.request
import urllib.error
from flask import Flask, jsonify, request, render_template
from datetime import datetime, timedelta
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import didkit
import json
import hashlib

# Iniciar la aplicación Flask.
app = Flask(__name__)

# Direcciones de los actores con contacto.
blockchain_url = 'http://nodo_principal:8545'
verificador_url = "http://verificador:5003"


class Emisor:
    def __init__(self):
        self.key = didkit.generate_ed25519_key()
        self.did = didkit.key_to_did("key", self.key)

        self.cuenta = "0x627306090abaB3A6e1400e9345bC60c78a8BEf57"
        self.clave_priv = "c87509a1c067bbde78beb793e6fa76530b6382a4c0241e5e4a9ec0a0f44dc0d3"

        self.contrato_desplegado = False

        # Variables para la monitorización.
        self.credencial = None
        self.dir_contrato = None
        self.tx_recibo = None
        self.hash_credencial = None
        self.hash_blockchain = None

    def crear_credencial(self, titular_did):
        credencial = {
            "@context": [
                "https://www.w3.org/ns/credentials/v2",
                "https://www.w3.org/ns/credentials/examples/v2",
            ],
            "type": ["VerifiableCredential", "CredencialPoC"],
            "issuer": self.did,
            "validFrom": datetime.now().isoformat(),
            "validUntil": (datetime.now() + timedelta(hours=1)).isoformat(),
            "credentialSubject": {
                "id": titular_did,
                "NombreActor": "Titular",
            },
        }
        return credencial

    def desplegar_contrato(self, w3, abi, bytecode, nonce):
        # Creación del contrato a partir del abi y bytecode.
        nuevo_contrato = w3.eth.contract(bytecode=bytecode, abi=abi)
        tx = nuevo_contrato.constructor().build_transaction(
            {
                "chainId": 1337,
                "gasPrice": 500000000,
                'gas': 500000,
                "from": emisor.cuenta,
                "nonce": nonce,
            }
        )
        # Firmar la transacción, efectuarla y esperar a la confirmación.
        tx_firmada = w3.eth.account.sign_transaction(tx, emisor.clave_priv)
        tx_contrato_hash = w3.eth.send_raw_transaction(tx_firmada.raw_transaction)
        tx_recibo = w3.eth.wait_for_transaction_receipt(tx_contrato_hash)
        self.dir_contrato = tx_recibo.contractAddress

        # Comunicar la dirección del contrato al Verificador.
        datos_raw = {'dir_contrato': emisor.dir_contrato}
        datos_bytes = json.dumps(datos_raw).encode('utf-8')
        peticion = emisor.realizar_peticion(verificador_url + '/recibir_direccion_contrato', datos_bytes, 'POST')

        # Comprobar el código de la respuesta.
        respuesta = urllib.request.urlopen(peticion)
        codigo_estado = respuesta.getcode()

        if codigo_estado == 200:
            # Controlar llamadas futuras.
            self.contrato_desplegado = True
            # Aumentar las transacciones realizadas.
            return nonce + 1

    def guardar_blockchain(self, w3, titular_did, credencial):
        # Obtener el abi desde el fichero local.
        with open('contrato.abi', 'r') as abi_file:
            abi = json.load(abi_file)

        # Obtener el bytecode desde el fichero local.
        with open('contrato.bin', 'r') as archivo_bytecode:
            bytecode = archivo_bytecode.read()

        # Obtener el número de transacciones actual de la cuenta.
        nonce = w3.eth.get_transaction_count(self.cuenta)
        if not self.contrato_desplegado:
            # El despligue del contrato solo se realiza la primera vez.
            nonce = self.desplegar_contrato(w3, abi, bytecode, nonce)

        # Creación de la instancia del contrato.
        contrato_credenciales = w3.eth.contract(address=self.dir_contrato, abi=abi)
        # Generar el hash de la credencial creada.
        self.hash_credencial = hashlib.sha256(json.dumps(credencial, sort_keys=True).encode('utf-8')).digest()

        # Construir la transacción con la operación para guardar el DID junto con el hash de la credencial.
        tx = contrato_credenciales.functions.registrarCredencial(titular_did, self.hash_credencial).build_transaction(
            {
                'chainId': 1337,
                'gasPrice': 500000000,
                'gas': 500000,
                "from": emisor.cuenta,
                'nonce': nonce,
            }
        )
        # Firmar la transacción, efectuarla y esperar a la confirmación.
        tx_firmada = w3.eth.account.sign_transaction(tx, emisor.clave_priv)
        tx_hash = w3.eth.send_raw_transaction(tx_firmada.raw_transaction)
        self.tx_recibo = w3.eth.wait_for_transaction_receipt(tx_hash)
        self.hash_blockchain = contrato_credenciales.functions.obtenerHashCredencial(titular_did).call()

    def realizar_peticion(self, url_completa, datos_bytes, metodo):
        return urllib.request.Request(
            url=url_completa,
            headers={'Content-Type': 'application/json'},
            data=datos_bytes,
            method=metodo,
        )


@app.route('/', methods=['GET'])  # http://127.0.0.1:5001
def inicio():
    return render_template('emisor.html', emisor=emisor)


###################################################
# Endpoints compartidos por las Pruebas de Concepto
###################################################

@app.route('/generar_credencial', methods=['POST'])  # Paso 1.
def generar_credencial():
    # Establecer la conexión con la blockchain.
    w3 = Web3(Web3.HTTPProvider(blockchain_url))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    # Comprobar que la blockchain está operativa.
    if w3.is_connected():
        # Obtener los datos de la petición.
        datos = request.get_json()
        titular_did = str(datos['did'])

        # Realizar las acciones pertinentes.
        emisor.credencial = emisor.crear_credencial(titular_did)
        emisor.guardar_blockchain(w3, titular_did, emisor.credencial)

        # Comunicar la resolución definitiva.
        return jsonify(emisor.credencial), 200
    else:
        return jsonify({"Respuesta": "La conexion a la Blockchain **NO** pudo efectuarse."}), 400


if __name__ == "__main__":
    emisor = Emisor()
    app.run(host='0.0.0.0', port=5001)
