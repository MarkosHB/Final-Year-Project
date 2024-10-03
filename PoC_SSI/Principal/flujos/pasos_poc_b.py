import urllib.request
import urllib.error
from flask import jsonify

# Necesario para monitorizar las comunicaciones.
titular_url = "http://titular:5002"


class PasosPocB:
    def __init__(self, aplicacion):
        self.app = aplicacion
        self.pasos()

    def realizar_peticion(self, url, metodo):
        peticion = urllib.request.Request(url + metodo, method='GET')
        try:
            respuesta = urllib.request.urlopen(peticion)
            contenido = respuesta.read().decode('utf-8')

        except urllib.error.HTTPError as e:
            contenido_error = e.read().decode('utf-8')
            contenido = contenido_error

        return contenido

    def asociar_paso(self, paso):
        if paso == 1:
            return self.realizar_peticion(titular_url, '/pedir_credencial')

        elif paso == 2:
            return self.realizar_peticion(titular_url, '/obtener_acceso')

        elif paso == 3:
            return self.realizar_peticion(titular_url, '/acceder_servicio_directamente')

        else:
            return "Error: Paso no definido."

    def pasos(self):
        @self.app.route('/poc_b_paso/<int:paso>', methods=['POST'])
        def poc_b_paso(paso):
            mensaje = self.asociar_paso(paso)
            return jsonify({'Respuesta': mensaje})
