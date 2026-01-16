import sys
import os # uso de rutas y sistema de archivo
import webbrowser

from PyQt6 import QtWidgets
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent

# ------------------------------
# clase ventana Acerca (2)
# ------------------------------
class Acerca_class(QtWidgets.QDialog):
    def __init__(self,idioma):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # cargar GUI
        # 1. Obtiene la ruta absoluta de la carpeta donde está este archivo (src/)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # 2. Construye la ruta subiendo un nivel y entrando a /gui
        # '..' significa "subir una carpeta"
        file = f"acerca_{idioma}.ui"
        print(file)
        path_ui = os.path.join(BASE_DIR, "gui", file)

        # 3. Carga la interfaz
        if os.path.exists(path_ui):
            uic.loadUi(path_ui, self)
        else:
            print(f"Error: No se encontró el archivo UI en: {path_ui}")

        # Obtener el QTextBrowser (asegúrate de que el nombre coincida con el de Qt Designer)
        self.text_browser = self.findChild(QtWidgets.QTextBrowser, "textBrowser")

        if self.text_browser is None:
            raise ValueError("QTextBrowser was not found in the file .ui")

        # Desactivar la apertura de enlaces dentro del QTextBrowser
        self.text_browser.setOpenLinks(False)

        # Conectar la señal anchorClicked
        self.text_browser.anchorClicked.connect(self.abrir_enlace)

        # EVENTOS
        self.pushButton_aceptar.clicked.connect(self.close) # cerrar ventana

    def abrir_enlace(self, url):
        webbrowser.open(url.toString())


    def closeEvent(self, event: QCloseEvent):
        """Maneja el evento de cierre de la ventana"""
        print("⚠️  ventana Acerca cerrando...")
        event.accept()

# ---------------------------------------------
# Solo ejecuta si es el archivo principal
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Acerca_class("english")
    window.show()

    app.exec()
