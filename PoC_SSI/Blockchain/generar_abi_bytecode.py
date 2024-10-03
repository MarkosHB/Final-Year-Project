from solcx import install_solc
import solcx
import json

'''
    Objetivo:
    ---------
        El siguiente script genera el abi y bytecode asociados al contrato a desplegar.
        **Solo** es necesario si se realiza una modificación al contrato desplegado en la red.
        
    Modo de uso:
    ------------
        - Ejecutar el programa en el directorio donde se encuntre el contrato.sol
        - Sobreescribir los archivos contrato.abi y contrato.bin de las carpetas Emisor y Verificador.
'''

install_solc(version='0.7.0')

# Compilar el contrato y acceder a sus componentes.
compilado = solcx.compile_files("contrato.sol", solc_version="0.7.0")
interfaz = compilado['contrato.sol:ContratoCredenciales']

# Obtener abi y bytecode.
abi = interfaz['abi']
bytecode = interfaz['bin']

# Guardar el abi en fichero json.
with open('contrato.abi', 'w') as archivo_abi:
    json.dump(abi, archivo_abi, indent=4)

# Guardar el bytecode en un archivo binario.
with open('contrato.bin', 'w') as archivo_bytecode:
    archivo_bytecode.write(bytecode)
