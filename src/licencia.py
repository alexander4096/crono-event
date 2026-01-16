import sys
import os # uso de rutas y sistema de archivo
import webbrowser

from PyQt6 import QtWidgets
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent


# ------------------------------
# clase ventana 10 - Licencia
# ------------------------------
class Licencia_class(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # cargar GUI
        self.path_ui = "gui"  # ruta de ventana
        window_path_ppal = os.path.join(self.path_ui, "licencia.ui")
        uic.loadUi(window_path_ppal, self)

        # Establece el título de la ventana
        self.setWindowTitle("License GNU GPL")
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
        print("⚠️  ventana Licencia cerrando...")
        event.accept()

# ---------------------------------------------
# Solo ejecuta si es el archivo principal
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = Licencia_class()
    window.show()

    app.exec()
