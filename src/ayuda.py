# funciona !! 23/10/2024
import sys
import os # uso de rutas y sistema de archivo
import webbrowser

from PyQt6 import QtWidgets
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent
from translations import translation_manager        # manejador de idiomas

# ------------------------------
# clase ventana Ayuda (3)
# ------------------------------
class Ayuda_class(QtWidgets.QDialog):
    def __init__(self, idioma):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # cargar GUI
        # 1. Obtiene la ruta absoluta de la carpeta donde está este archivo (src/)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # 2. Construye la ruta subiendo un nivel y entrando a /gui
        # '..' significa "subir una carpeta"
        path_ui = os.path.join(BASE_DIR, "gui", "ayuda.ui")

        # 3. Carga la interfaz
        if os.path.exists(path_ui):
            uic.loadUi(path_ui, self)
        else:
            print(f"Error: No se encontró el archivo UI en: {path_ui}")



        # CARGAR el idioma de la ventana
        self.cargar_idioma(idioma)

        # Obtener el QTextBrowser (asegúrate de que el nombre coincida con el de Qt Designer)
        self.text_browser = self.findChild(QtWidgets.QTextBrowser, "textBrowser")

        if self.text_browser is None:
            raise ValueError("QTextBrowser was not found in the file .ui")

        # Desactivar la apertura de enlaces dentro del QTextBrowser
        self.text_browser.setOpenLinks(False)

        # Conectar la señal anchorClicked
        self.text_browser.anchorClicked.connect(self.abrir_enlace)

        # EVENTOS
        self.pushButton_cerrar.clicked.connect(self.close)  # cerrar ventana self.close




    # CARGAR el idioma de la ventana
    def cargar_idioma(self, idioma):
        self.current_language = idioma  # idioma por defecto
        self.ui = "ui_ayuda"  # nombre del JSON UI para la ventana edit_event
        self.message = "messages_ayuda"  # nombre del JSON mensaje
        translation_manager.set_language(self.current_language)  # actualizar idioma seleccionado
        translation_manager.set_name_ui(self.ui, self.message)
        self.update_texts()  # actualiza el texto del idioma seleccionado
        # -------------

    # PARA ABRIR Webbrowser
    def abrir_enlace(self, url):
        webbrowser.open(url.toString())

    # idioma de la ventana actualiza
    def update_texts(self):
        self.setWindowTitle(translation_manager.get_ui_text("window_title"))
        self.label_2.setText(translation_manager.get_ui_text("label_2"))
        self.pushButton_cerrar.setText(translation_manager.get_ui_text("pushButton_cerrar"))


    def closeEvent(self, event: QCloseEvent):
        """Maneja el evento de cierre de la ventana"""
        print("⚠️  ventana Ayuda cerrando...")
        event.accept()

# ---------------------------------------------
# Solo ejecuta si es el archivo principal
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = Ayuda_class("english")
    window.show()

    app.exec()
