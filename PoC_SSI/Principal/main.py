from flask import Flask, request, render_template
from flujos.pasos_poc_a import PasosPocA
from flujos.pasos_poc_b import PasosPocB

# Iniciar la aplicación Flask.
app = Flask(__name__)

# Redirigimos el flujo hacia la Prueba de Concepto correspondiente.
flujo_a = PasosPocA(app)
flujo_b = PasosPocB(app)


@app.route('/', methods=['GET', 'POST'])  # http://127.0.0.1:5000
def inicio():
    if request.method == 'POST':
        flujo = request.form.get('modo')
        if flujo == "A":
            return render_template('poc_a.html')
        elif flujo == "B":
            return render_template('poc_b.html')
    else:
        return render_template('index.html')  # GET


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
