pragma solidity ^0.7.0;

contract ContratoCredenciales {
    // Una única credencial por cada DID almacenado.
    mapping(string => bytes32) private credenciales;

    // Registrar un nuevo hash de la credencial asociada a su correspondiente DID.
    function registrarCredencial(string memory did, bytes32 hashCredencial) public {
        credenciales[did] = hashCredencial;
    }

    // Obtener el hash de la credencial correspondiente a su DID.
    function obtenerHashCredencial(string memory did) public view returns (bytes32) {
        return credenciales[did];
    }
}