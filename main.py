from lector_pdf import extraer_datos_remesa
from screaper import obtener_ubicacion_satrack

# Base de datos / Diccionario de credenciales por cliente
CUENTAS_SATRACK = {
    "METAL IDEAS COLOMBIA SAS": {
        "usuario": "santiago890",
        "contrasena": "Lopez890*"
    },
    # Agrega aquí más clientes y sus credenciales según los necesites
    "CLIENTE_EJEMPLO_SAS": {
        "usuario": "usuario_ejemplo",
        "contrasena": "clave_ejemplo"
    }
}

# Credenciales por defecto en caso de no encontrar coincidencia específica
CRED_DEFAULT = {
    "usuario": "santiago890",
    "contrasena": "Lopez890*"
}

def generar_reporte(archivo_pdf):
    print("1. Leyendo datos de la remesa en PDF...")
    datos_remesa = extraer_datos_remesa(archivo_pdf)
    placa = datos_remesa["placa"]
    destinatario = datos_remesa["destinatario"]
    
    # Seleccionar credenciales dinámicamente según el destinatario
    credenciales = CUENTAS_SATRACK.get(destinatario, CRED_DEFAULT)
    user_satrack = credenciales["usuario"]
    pass_satrack = credenciales["contrasena"]
    
    print(f"2. Consultando Satrack para la placa {placa} (Usuario: {user_satrack})...")
    info_satrack = obtener_ubicacion_satrack(
        placa=placa,
        usuario=user_satrack,
        contrasena=pass_satrack
    )
    
    print("\n" + "="*45)
    print("        REPORTE CONSOLIDADO DE REMESA")
    print("="*45)
    print(f"• Placa: {datos_remesa['placa']}")
    print(f"• Conductor: {datos_remesa['conductor']}")
    print(f"• Origen: {datos_remesa['origen']}")
    print(f"• Destino: {datos_remesa['destino']}")
    print(f"• Destinatario: {datos_remesa['destinatario']}")
    print("-" * 45)
    print("ESTADO EN TIEMPO REAL (SATRACK):")
    print(info_satrack if info_satrack else "No se pudo obtener información de la plataforma.")
    print("="*45 + "\n")

if __name__ == "__main__":
    generar_reporte("REMESA.pdf")

