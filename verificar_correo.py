import sys
import requests
import time
import os
import getpass
import logging
import csv

# Configuración de logging
logging.basicConfig(
    filename="registro.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Validación de argumentos
if len(sys.argv) != 2:
    print("Uso: python verificar_correo.py correo@example.com")
    sys.exit(1)

correo = sys.argv[1]

# Lectura segura de API key
if not os.path.exists("apikey.txt"):
    print("🔐 No se encontró el archivo apikey.txt.")
    clave = getpass.getpass("Ingresa tu API key: ")
    try:
        with open("apikey.txt", "w") as archivo:
            archivo.write(clave.strip())
    except Exception as e:
        logging.error("Error al guardar la API key: %s", e)
        sys.exit(1)

try:
    with open("apikey.txt", "r") as archivo:
        api_key = archivo.read().strip()
except Exception as e:
    print("Error al leer la API key.")
    logging.error("Error al leer la API key: %s", e)
    sys.exit(1)

# Consulta principal
url = (
    f"https://haveibeenpwned.com/api/v3/breachedaccount/{correo}"
)
headers = {
    "hibp-api-key": api_key,
    "user-agent": "PythonScript"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    brechas = response.json()
    logging.info(
        "Consulta exitosa para %s. Brechas encontradas: %d",
        correo, len(brechas)
    )

    try:
        with open("reporte.csv", "w", newline='', encoding="utf-8") as archivo_csv:
            writer = csv.writer(archivo_csv)
            writer.writerow([
                "Título", "Dominio", "Fecha de Brecha",
                "Datos Comprometidos", "Verificada", "Sensible"
            ])

            for i, brecha in enumerate(brechas[:3]):
                nombre = brecha['Name']
                detalle_url = (
                    f"https://haveibeenpwned.com/api/v3/breach/{nombre}"
                )
                detalle_resp = requests.get(detalle_url, headers=headers)

                if detalle_resp.status_code == 200:
                    detalle = detalle_resp.json()
                    writer.writerow([
                        detalle.get('Title'),
                        detalle.get('Domain'),
                        detalle.get('BreachDate'),
                        ', '.join(detalle.get('DataClasses', [])),
                        detalle.get('IsVerified'),
                        detalle.get('IsSensitive')
                    ])
                else:
                    logging.error(
                        "No se pudo obtener detalles de la brecha: %s",
                        nombre
                    )

                if i < 2:
                    time.sleep(10)

    except Exception as e:
        logging.error("Error al escribir reporte.csv: %s", e)
        print("Error al generar el reporte CSV.")

elif response.status_code == 404:
    logging.info(
        "Consulta exitosa %s. No se encontro brechas.",
        correo
    )
    print(f"La cuenta {correo} no aparece en ninguna brecha conocida.")

elif response.status_code == 401:
    logging.error("Error 401: API key inválida.")
    print("Error de autenticación: revisa tu API key.")

else:
    logging.error(
        "Error inesperado. Código de estado: %d",
        response.status_code
    )
    print(f"Error inesperado. Código de estado: {response.status_code}")