# funciona !! 23/10/2024
import sys
import os # uso de rutas y sistema de archivo
from PyQt6 import QtWidgets
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette, QCloseEvent
import configuracion as config                      # lee y escribe configuracion del programa

# ------------------------------
# clase ventana VerAlarma (9)
# ------------------------------
class VerAlarma_class(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # cargar GUI
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # 2. Construye la ruta subiendo un nivel y entrando a /gui
        # '..' significa "subir una carpeta"
        path_ui = os.path.join(BASE_DIR, "gui", "ver_alarma.ui")

        # 3. Carga la interfaz
        if os.path.exists(path_ui):
            uic.loadUi(path_ui, self)
        else:
            print(f"Error: No se encontró el archivo UI en: {path_ui}")


        # Establece el título de la ventana
        self.setWindowTitle("Ver Alarma")

        # LEER configuracion
        self.correr_configuracion()

    # leer configuracion y poner valores en el widget
    def correr_configuracion(self):
        self.configData = config.leer_configuracion()
        item = "font_evento"
        font = QFont()
        font.setFamily(self.configData[item]["family"])
        font.setPointSize(self.configData[item]["point_size"])
        font.setWeight(self.configData[item]["weight"])
        font.setItalic(self.configData[item]["italic"])
        font.setUnderline(self.configData[item]["underline"])
        font.setStrikeOut(self.configData[item]["strikeout"])
        font.setBold(self.configData[item]["bold"])
        self.lineEdit_verAlarma.setFont(font)

    def closeEvent(self, event: QCloseEvent):
        """Maneja el evento de cierre de la ventana"""
        print("⚠️  ventana Ver Alarma cerrando...")
        event.accept()

    # poner valor en pantalla de alarma
    def valor_alarma(self, texto):
        self.lineEdit_verAlarma.setText(f"{texto}")

    # poner color de fondo bg de lineEdit
    def poner_color_fondo(self, color):
        palette = self.lineEdit_verAlarma.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(color))
        self.lineEdit_verAlarma.setPalette(palette)



# ---------------------------------------------
# Solo ejecuta si es el archivo principal
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = VerAlarma_class()
    window.show()

    app.exec()
