import sys
from PyQt6 import QtWidgets, uic


class MiVentana(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # 1. Cargar el archivo .ui
        # Asegúrate de que el archivo 'interfaz.ui' esté en la misma carpeta

        uic.loadUi("cronometroV2.ui", self)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    ventana = MiVentana()
    ventana.show()

    sys.exit(app.exec())