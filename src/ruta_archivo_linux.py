import os
import sys

# FOR LINUX
# Nombre de tu aplicación / configuracion / ruta de eventos
APP_NAME = "crono-event"
APP_NAME_CONFIG = "config.ini"
APP_PATH_EVENTS = "events"

# Obtener la ruta base para configuración del usuario
config_dir = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
print(f"config_dir = {config_dir}")

# Ruta para la configuración de la aplicación
app_config_dir = os.path.join(config_dir, APP_NAME)
print(f"app_config_dir = {app_config_dir}")

# Ruta para el subdirectorio "events"
events_dir = os.path.join(app_config_dir, "events")
print(f"events_dir = {events_dir}")

# Ruta al archivo config.ini (directamente en ~/.config/crono-event/)
config_file = os.path.join(app_config_dir, APP_NAME_CONFIG)
print(f"config_file = {config_file}")

# Crear los directorios si no existen
os.makedirs(app_config_dir, exist_ok=True) # directorio de apps
os.makedirs(events_dir, exist_ok=True)     # directorio de evento

"""
config_dir = /home/alex/.config
app_config_dir = /home/alex/.config/crono-event
events_dir = /home/alex/.config/crono-event/events
config_file = /home/alex/.config/crono-event/config.ini
"""

# funcion para ruta en flatpack
def obtener_ruta_base():
    # 1. ¿Estamos dentro de un entorno Flatpak?
    if os.path.exists('/.flatpak-info') or 'FLATPAK_ID' in os.environ:
        # En Flatpak, tus archivos instalados están en /app/bin o /app/share/tu-app
        # Como en tu YAML pusiste los archivos en /app/bin, usamos esa:
        return "/app/bin"

    # 2. ¿Es un binario de PyInstaller (fuera de Flatpak)?
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS

    # 3. ¿Es ejecución normal desde el código fuente (.py)?
    return os.path.dirname(os.path.realpath(__file__))


# Configuración de rutas globales
BASE_DIR = obtener_ruta_base()
RUTA_GUI = os.path.join(BASE_DIR, "gui")
RUTA_WAV = os.path.join(BASE_DIR, "wav")
RUTA_TRADUCCIONES = os.path.join(BASE_DIR, "translations")