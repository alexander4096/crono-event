import json
import os

# clase para leer los idiomas
class TranslationManager:
    def __init__(self):
        # inicializar variables
        self.translations = {} # variable contenedora de las traducciones
        self.current_language = "english"
        self.ui = "ui_edit_crono"
        self.message = "messages_edit_crono"
        self.lista_idiomas = []  # lista de idiomas en subdirectorio

    # muestra la lista de idiomas disponibles
    def listado_idiomas(self):
        self.lista_idiomas = []
        translations_dir = os.path.dirname(__file__)  # path completo de la ruta de idioma
        for filename in os.listdir(translations_dir):
            # solo los archivos json
            if filename.endswith('.json'):
                # lee cada uno de los archivos
                lang_name = filename.split('.')[0]
                self.lista_idiomas.append(lang_name)
        self.lista_idiomas.sort()
        return  self.lista_idiomas

    # poner nombre de UI de ventana y mensaje de ventana para saber cual bloque  de JSON leer
    def set_name_ui(self, ui, message):
        self.ui = ui
        self.message = message

    # poner el idioma a usar
    def set_language(self, language):
        """Establecer el idioma actual"""
        translations_dir = os.path.dirname(__file__)  # path completo de la ruta de idioma
        file_path = os.path.join(translations_dir, f"{language}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # carga cada uno de los idiomas
                self.translations = json.load(file)
                # print(self.translations)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")


    # leer el idima para el widget
    def get_ui_text(self, key):
        try:
            # por el momento la categoria es ui
            return self.translations[self.ui][key]
        except KeyError as e:
            # Clave no encontrada en JSON
            print(f"❌ Error: Clave '{key}' no encontrada en traducciones")
            return "<None>"

    # leer el idioma para el mensaje
    def get_message(self, key):
        try:
            """Obtener texto de mensajes"""
            return self.translations[self.message][key]
        except KeyError as e:
            # Clave no encontrada en JSON
            print(f"❌ Error: Clave '{key}' no encontrada en traducciones")
            return "<None>"


# Instancia global del gestor de traducciones
translation_manager = TranslationManager()

