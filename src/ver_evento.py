# funciona !! 23/10/2024
import sys
import os # uso de rutas y sistema de archivo
from PyQt6 import QtWidgets
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette, QCloseEvent
import configuracion as config                      # lee y escribe configuracion del programa

# ------------------------------
# clase ventana VerEvento (8)
# ------------------------------
class VerEvento_class(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # cargar GUI
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # 2. Construye la ruta subiendo un nivel y entrando a /gui
        # '..' significa "subir una carpeta"
        path_ui = os.path.join(BASE_DIR, "gui",  "ver_evento.ui")

        # 3. Carga la interfaz
        if os.path.exists(path_ui):
            uic.loadUi(path_ui, self)
        else:
            print(f"Error: No se encontró el archivo UI en: {path_ui}")


        self.pos_evento = []
        self.size_window = []
        # Establece el título de la ventana
        self.setWindowTitle("Evento")

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
        self.lineEdit_verEvento.setFont(font)


    # captura evento de movimento de ventana
    def moveEvent(self, event):
        new_pos = event.pos()  # Obtiene la nueva posición de la ventana
        print(f"V.Evento movido: ({new_pos.x()}, {new_pos.y()})")
        self.pos_evento = [new_pos.x(), new_pos.y()]  # asignar valores de pos vent ppal

    def resizeEvent(self, event):
        """ Override the resizeEvent method to handle window resize events. """
        initial_size = self.size()
        print(f"Initial window size: {initial_size.width()} x {initial_size.height()}")
        self.size_window =[initial_size.width(), initial_size.height()]

    def optener_size_ventana(self):
        initial_size = self.size()
        print(f"window ver Evento size: {initial_size.width()} x {initial_size.height()}")
        self.size_window =[initial_size.width(), initial_size.height()]
        return self.size_window

    # optener posicion de ventana ver evento
    def optener_pos_vent(self):
        pos = self.pos()
        print(f"Posición actual de la ventana: {pos.x()}, {pos.y()}")
        self.pos_evento = [pos.x(), pos.y()]  # asignar valores de pos vent ppal
        return self.pos_evento

    # pone titulo de actividad del evento
    def poner_actividad(self, titulo):
        self.lineEdit_verEvento.setText(str(titulo))

    # poner color de fondo bg de lineEdit
    def poner_color_fondo(self, color):
        palette = self.lineEdit_verEvento.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(color))
        self.lineEdit_verEvento.setPalette(palette)

    # pone el titulo de la ventana
    def poner_titulo_ventana(self, titulo):
        self.setWindowTitle(str(titulo))



    def closeEvent(self, event: QCloseEvent):
        """Maneja el evento de cierre de la ventana"""
        print("⚠️  ventana Evento cerrando...")
        event.accept()



# ---------------------------------------------
# Solo ejecuta si es el archivo principal
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = VerEvento_class()
    window.show()

    app.exec()
