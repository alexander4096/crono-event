import json
import os
import ruta_archivo_linux as datafile

# Nombre del archivo de configuración
CONFIG_FILE = datafile.config_file


# datos de configuracion inicial
def configuracion_inicial():
    return {
        "general": {
            "languaje": "english",
            "gui_path": "gui"
        },
        "ventana_ppal": {
            "pos_xy": [272, 501],
            "size": [350, 150]
        },
        "ventana_evento": {
            "pos_xy": [272, 501],
            "size": [472, 150]
        },
        "font_crono": {
            'family': 'Noto Sans',
            'point_size': 14,
            'weight': 400,
            'italic': False,
            'underline': False,
            'strikeout': False,
            'bold': False
        },
        "color_crono": {
            'texto': '#55aa7f',
            'fondo': '#ffffff'
        },
        "font_evento": {
            'family': 'Noto Sans',
            'point_size': 14,
            'weight': 400,
            'italic': False,
            'underline': False,
            'strikeout': False,
            'bold': False
        },
        "font_alarma": {
            'family': 'Noto Sans',
            'point_size': 14,
            'weight': 400,
            'italic': False,
            'underline': False,
            'strikeout': False,
            'bold': False
        }
    }


def guardar_configuracion(datos=None):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        print(f"Configuración guardada en {CONFIG_FILE}")
    except Exception as e:
        print(f"Error guardando configuración: {e}")


def leer_configuracion():
    """
    Lee la configuración desde el archivo JSON.
    Si el archivo no existe, está vacío o es inválido,
    devuelve la configuración inicial y guarda un nuevo archivo.
    """
    # Verificar si el archivo existe
    if not os.path.exists(CONFIG_FILE):
        print(f"Archivo de configuración no encontrado. Creando uno nuevo.")
        config = configuracion_inicial()
        guardar_configuracion(config)
        return config

    # Verificar si el archivo está vacío
    if os.path.getsize(CONFIG_FILE) == 0:
        print(f"Archivo de configuración vacío. Usando valores por defecto.")
        config = configuracion_inicial()
        guardar_configuracion(config)
        return config

    try:
        # Intentar leer el archivo
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            contenido = f.read()

            # Si el contenido está vacío después de leer
            if not contenido.strip():
                print(f"Archivo vacío después de leer. Usando valores por defecto.")
                config = configuracion_inicial()
                guardar_configuracion(config)
                return config

            # Intentar parsear el JSON
            config_data = json.loads(contenido)
            print(f"Configuración leída correctamente de {CONFIG_FILE}")
            return config_data

    except json.JSONDecodeError as e:
        print(f"Error de JSON en el archivo de configuración: {e}")
        print("Usando configuración por defecto.")
        config = configuracion_inicial()
        guardar_configuracion(config)
        return config

    except Exception as e:
        print(f"Error inesperado leyendo configuración: {e}")
        print("Usando configuración por defecto.")
        return configuracion_inicial()


# Ejemplo de uso:
if __name__ == "__main__":
    # Leer del archivo (si no existe o hay error, usa valores iniciales)
    data = leer_configuracion()
    print(f"Configuración cargada: {data}")