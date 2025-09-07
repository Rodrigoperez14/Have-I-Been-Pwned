import time
import logging
import funciones

if __name__ == "__main__":
    args = funciones.obtener_argumentos()
    correo = args.correo
    salida = args.output
    api_key = funciones.leer_apikey()

    try:
        respuesta = funciones.consultar_brechas(correo, api_key)
    except Exception as e:
        logging.error("Error de conexión: %s", e)
        exit()

    if respuesta.status_code == 200:
        brechas = respuesta.json()
        logging.info(
            "%s comprometido en %d brechas.",
            correo, len(brechas)
        )
        detalles = []

        for i, brecha in enumerate(brechas[:3]):
            nombre = brecha["Name"]
            detalle_resp = funciones.consultar_detalle(nombre, api_key)

            if detalle_resp.status_code == 200:
                detalles.append(detalle_resp.json())
            else:
                logging.error(
                    "No se pudo obtener detalles de %s. Código: %d",
                    nombre, detalle_resp.status_code
                )

            if i < 2:
                time.sleep(10)

        funciones.generar_csv(salida, detalles)
        print(f"Consulta completada. Revisa el archivo {salida}.")

    elif respuesta.status_code == 404:
        logging.info("%s no aparece en brechas conocidas.", correo)
        print(f"La cuenta {correo} no aparece en ninguna brecha.")

    elif respuesta.status_code == 401:
        logging.error("API key inválida.")
        print("Error de autenticación.")

    else:
        logging.error("Error inesperado. Código: %d", respuesta.status_code)
        print(f"Error inesperado. Código: {respuesta.status_code}")