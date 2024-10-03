document.addEventListener('DOMContentLoaded', () => {
    const avanzarPaso = async (paso, poc) => {
        const respuesta = await fetch(`/poc_${poc}_paso/${paso}`, {method: 'POST'});
        const contenido = await respuesta.json();
        const contenedor_mensaje = document.querySelector(`#consola`);
        contenedor_mensaje.innerHTML = contenido["Respuesta"];
    };

    document.querySelectorAll('.boton-general').forEach(button => {
        button.addEventListener('click', () => {
            const paso = button.getAttribute('numero-paso');
            const poc = button.getAttribute('poc');
            avanzarPaso(paso, poc);
        });
    });
});
