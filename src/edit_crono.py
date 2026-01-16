# funciona !! 23/10/2024
import sys
import os # uso de rutas y sistema de archivo
from PyQt6 import QtWidgets
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMessageBox
from translations import translation_manager # manejador de idiomas

from PyQt6.QtCore import QTimer, QElapsedTimer

# ------------------------------
# clase ventana EDITAR CRONO (1)
# ------------------------------
class EditarCrono_class(QtWidgets.QDialog):
    def __init__(self,  main_window, idioma):
        super().__init__()
        self.main_window = main_window  # Guarda la referencia a la instancia de A
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # cargar GUI
        # 1. Obtiene la ruta absoluta de la carpeta donde está este archivo (src/)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # 2. Construye la ruta subiendo un nivel y entrando a /gui
        # '..' significa "subir una carpeta"
        path_ui = os.path.join(BASE_DIR, "gui", "edit_crono.ui")

        # 3. Carga la interfaz
        if os.path.exists(path_ui):
            uic.loadUi(path_ui, self)
        else:
            print(f"Error: No se encontró el archivo UI en: {path_ui}")


        # CARGAR el idioma de la ventana
        self.cargar_idioma(idioma) # idioma

        self.lineEdit_crono_edit.setInputMask("00:00:00; ") # mascara

        # Establece el título de la ventana
        self.show()

        # inicializar variable
        self.selected_item = ""
        self.hh_int = 0
        self.mm_int = 0
        self.ss_int = 0

        self.comboBox_modo_crono.setCurrentIndex(0)  # Set "Default Option" as default 0 - 2


        # EVENTO BOTONES
        self.pushButton_limpiar.clicked.connect(self.limpiar_display)          # btn limpiar
        self.pushButton_aplicar.clicked.connect(self.aplicar)          # btn aplicar
        self.pushButton_actualizar.clicked.connect(self.leer_display)  # btn actualizar
        # Evento combo box
        self.comboBox_modo_crono.currentIndexChanged.connect(self.leer_display)



        # --------------------------------------------------------------
        # 1. Crear timer para incremento fijo
        self.timer_incremento = QTimer()
        self.timer_incremento.timeout.connect(self.incrementar_valor)
        self.boton = ""

        # 2. ESTABLECER VELOCIDAD FIJA (en milisegundos)
        self.intervalo_fijo = 100  # 100ms = 10 incrementos por segundo
        self.timer_incremento.setInterval(self.intervalo_fijo)

        # botones basculantes para configurar tiempo
        # Conectar botón up_hh
        self.pushButton_up_hh.pressed.connect(lambda: self.cuando_presionado("up_hh"))
        self.pushButton_up_hh.released.connect(self.cuando_liberado)
        # Conectar botón dw_hh
        self.pushButton_dw_hh.pressed.connect(lambda: self.cuando_presionado("dw_hh"))
        self.pushButton_dw_hh.released.connect(self.cuando_liberado)
        # Conectar botón up_mm
        self.pushButton_up_mm.pressed.connect(lambda: self.cuando_presionado("up_mm"))
        self.pushButton_up_mm.released.connect(self.cuando_liberado)
        # Conectar botón dw_mm
        self.pushButton_dw_mm.pressed.connect(lambda: self.cuando_presionado("dw_mm"))
        self.pushButton_dw_mm.released.connect(self.cuando_liberado)
        # Conectar botón up_ss
        self.pushButton_up_ss.pressed.connect(lambda: self.cuando_presionado("up_ss"))
        self.pushButton_up_ss.released.connect(self.cuando_liberado)
        # Conectar botón dw_ss
        self.pushButton_dw_ss.pressed.connect(lambda: self.cuando_presionado("dw_ss"))
        self.pushButton_dw_ss.released.connect(self.cuando_liberado)



    def cuando_presionado(self, boton):
        self.boton = boton
        print(f"Botón presionado = {self.boton}")
        self.timer_incremento.start()

    def cuando_liberado(self):
        # Detener el timer
        self.timer_incremento.stop()

    def incrementar_valor(self):

        # tomar el tiempo del lineEdit
        time_str = self.lineEdit_crono_edit.text()
        # Separar hh, mm, ss
        hh, mm, ss = time_str.split(":")

        # Validar los valores
        self.hh_int = int(hh)
        self.mm_int = int(mm)
        self.ss_int = int(ss)

        # PARA HORA
        if self.boton == "up_hh":
            self.hh_int += 1
            self.hh_int = 0 if self.hh_int >= 99 else self.hh_int
        if self.boton == "dw_hh":
            self.hh_int -= 1
            self.hh_int = 99 if self.hh_int <= 0 else self.hh_int

        # PARA MINUTO
        if self.boton == "up_mm":
            self.mm_int += 1
            self.mm_int = 00 if self.mm_int >= 60 else self.mm_int
        if self.boton == "dw_mm":
            self.mm_int -= 1
            self.mm_int = 59 if self.mm_int <= -1 else self.mm_int

        # PARA SEGUNDO
        if self.boton == "up_ss":
            self.ss_int += 1
            self.ss_int = 00 if self.ss_int >= 60 else self.ss_int
        if self.boton == "dw_ss":
            self.ss_int -= 1
            self.ss_int = 59 if self.ss_int <= -1 else self.ss_int


        # SALIDA por LineEdit
        self.lineEdit_crono_edit.setText(f"{self.hh_int:02d}:{self.mm_int:02d}:{self.ss_int:02d}")


    # -------------------------------------------------------------------
    # CARGAR el idioma de la ventana
    def cargar_idioma(self, idioma):
        self.current_language = idioma  # idioma por defecto
        self.ui = "ui_edit_crono"  # nombre del JSON UI para la ventana edit_event
        self.message = "messages_edit_crono"  # nombre del JSON mensaje para la ventna edit_event
        translation_manager.set_language(self.current_language)  # actualizar idioma seleccionado
        translation_manager.set_name_ui(self.ui, self.message)
        self.update_texts()  # actualiza el texto del idioma seleccionado
        # ---------

    # idioma de la ventana actualiza
    def update_texts(self):
        self.setWindowTitle(translation_manager.get_ui_text("window_title"))
        self.label_1.setText(translation_manager.get_ui_text("label_1"))
        self.label_2.setText(translation_manager.get_ui_text("label_2"))
        self.label_3.setText(translation_manager.get_ui_text("label_3"))
        self.label_4.setText(translation_manager.get_ui_text("label_4"))

        self.pushButton_actualizar.setText(translation_manager.get_ui_text("pushButton_actualizar"))
        self.pushButton_limpiar.setText(translation_manager.get_ui_text("pushButton_limpiar"))
        self.pushButton_aplicar.setText(translation_manager.get_ui_text("pushButton_aplicar"))
        self.comboBox_modo_crono.addItems(translation_manager.get_ui_text("comboBox_modo_crono"))




    def closeEvent(self, event: QCloseEvent):
        """Maneja el evento de cierre de la ventana"""
        print("⚠️  ventana Editar Crono cerrando...")
        event.accept()

    # metodo de combobox
    def leer_display(self):
        print("combobox edit crono")
        self.selected_item = self.comboBox_modo_crono.currentText()
        self.index = self.comboBox_modo_crono.currentIndex()
        print(f"combo index ={self.index} {self.selected_item}")

        if not self.main_window is None:  # si existe clase main_window ejecuta el metodo
            if self.index == 0: #  "Progresivo"
                self.hh_int = self.main_window.tiempo_progresivo[0]["hora"]
                self.mm_int = self.main_window.tiempo_progresivo[0]["minuto"]
                self.ss_int = self.main_window.tiempo_progresivo[0]["segundo"]

            if self.index == 1: #  "Regresivo"
                self.hh_int = self.main_window.tiempo_regresivo[0]["hora"]
                self.mm_int = self.main_window.tiempo_regresivo[0]["minuto"]
                self.ss_int = self.main_window.tiempo_regresivo[0]["segundo"]

            if self.index == 2: #  "Evento"
                self.hh_int = self.main_window.tiempo_evento[0]["hora"]
                self.mm_int = self.main_window.tiempo_evento[0]["minuto"]
                self.ss_int = self.main_window.tiempo_evento[0]["segundo"]

            # poner hora del display en editor crono
            formateado = f"{self.hh_int:02d}:{self.mm_int:02d}:{self.ss_int:02d}"
            self.lineEdit_crono_edit.setText(formateado)  # Valor inicial
        else:
            QMessageBox.information(
                self,
                "Error",
                "No se puede LEER datos \nen pantalla de cronometro"
            )



    # Metodos de btn (PONER VALOR A CAMPOS CHRONOMETROS)
    def poner_valor_a_display(self):
        if not self.main_window is None:  # si existe clase main_window ejecuta el metodo
            self.index = self.comboBox_modo_crono.currentIndex()
            print(f"combo index ={self.index} {self.selected_item}")

            if self.index == 0:  # "Progresivo"
                self.main_window.tiempo_progresivo[0]["hora"] =    self.hh_int
                self.main_window.tiempo_progresivo[0]["minuto"] =  self.mm_int
                self.main_window.tiempo_progresivo[0]["segundo"] = self.ss_int

            if self.index == 1: # "Regresivo"
                self.main_window.tiempo_regresivo[0]["hora"] = self.hh_int
                self.main_window.tiempo_regresivo[0]["minuto"] = self.mm_int
                self.main_window.tiempo_regresivo[0]["segundo"] = self.ss_int

            if self.index == 2: # "Evento"
                self.main_window.tiempo_evento[0]["hora"] = self.hh_int
                self.main_window.tiempo_evento[0]["minuto"] = self.mm_int
                self.main_window.tiempo_evento[0]["segundo"] = self.ss_int
        else:
            QMessageBox.information(
                self,
                "Error",
                "No se puede PONER datos \nen pantalla de cronometro"
            )

    # Metodos de btn
    def limpiar_display(self):
        print("btn limpiar")
        self.lineEdit_crono_edit.setText("00:00:00")  # Valor inicial

    # poner cambios en respectivos chronometros
    def aplicar(self):
        print("btn aplicar")
        # Obtener el texto del QLineEdit
        time_str = self.lineEdit_crono_edit.text()

        try:
            # Separar hh, mm, ss
            hh, mm, ss = time_str.split(":")

            # Validar los valores
            self.hh_int = int(hh)
            self.mm_int = int(mm)
            self.ss_int = int(ss)

            if self.hh_int > 99 or self.mm_int > 59 or self.ss_int > 59:
                QMessageBox.warning(
                    self,
                    "Error de validación",
                    "Los valores no pueden exceder:\n"
                    "- hh: 99\n"
                    "- mm: 59\n"
                    "- ss: 59"
                )
                return

            # poner nuevo tiempo editado al chronometro seleccionado
            self.selected_item = self.comboBox_modo_crono.currentText()
            self.label_4.setText(f"{self.selected_item} "
                                      f"hh: {self.hh_int:02d}, "
                                      f"mm: {self.mm_int:02d}, "
                                      f"ss: {self.ss_int:02d}")
            self.poner_valor_a_display() # aplicar cambio a display

        except ValueError:
            QMessageBox.warning(
                self,
                "Error de formato",
                "Por favor, ingrese un formato válido (hh:mm:ss)."
            )




# ---------------------------------------------
# Solo ejecuta si es el archivo principal
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = EditarCrono_class(None, "english")
    app.exec()