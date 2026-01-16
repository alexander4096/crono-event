import sys
import os # uso de rutas y sistema de archivo
from PyQt6 import QtWidgets
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QFont, QPalette, QColor
from PyQt6.QtWidgets import QFontDialog, QColorDialog, QFileDialog, QMessageBox
from translations import translation_manager        # manejador de idiomas
import configuracion as config                      # lee y escribe configuracion del programa
import ruta_archivo_linux as rutas                  # leer rutas

# ------------------------------
# clase ventana edit_config
# ------------------------------
class EditConfig_class(QtWidgets.QDialog):
    def __init__(self,  main_window, idioma):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.main_window = main_window  # Guarda la referencia a la instancia de A

        # inicializar variable
        self.font_configs = {}
        self.font_Alarm = {}
        self.font_Crono = {}
        self.font_Event = {}
        self.colorFondo = None
        self.colorTexto = None
        self.ruta_GUI_Crono = ""

        # cargar GUI
        # 1. Obtiene la ruta absoluta de la carpeta donde está este archivo (src/)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # 2. Construye la ruta subiendo un nivel y entrando a /gui
        # '..' significa "subir una carpeta"
        path_ui = os.path.join(BASE_DIR, "gui", "edit_config.ui")

        # 3. Carga la interfaz
        if os.path.exists(path_ui):
            uic.loadUi(path_ui, self)
        else:
            print(f"Error: No se encontró el archivo UI en: {path_ui}")


        self.show()

        self.cargar_idioma(idioma)  # CARGAR el idioma de la ventana
        self.cargar_configuracion()  # cargar configuracion y poner idioma

        # EVENTOS
        self.pushButton_cerrar.clicked.connect(self.close)    # cerrar ventana self.close
        self.pushButton_guardar.clicked.connect(self.guardar) # guardar
        self.comboBox_idioma.activated.connect(self.seleccion_idioma)  # seleccion
        self.pushButton_fontCrono.clicked.connect(lambda: self.aplicarFondo("crono"))  # cambiar fondo de Crono
        self.pushButton_fontEvent.clicked.connect(lambda: self.aplicarFondo("evento")) # cambiar fondo evento
        self.pushButton_fontAlarm.clicked.connect(lambda: self.aplicarFondo("alarma")) # cambiar fondo alarma
        self.pushButton_colorTexto.clicked.connect(lambda: self.aplicarColor("textoCrono"))  #  cambia color texto crono
        self.pushButton_colorFondo.clicked.connect(lambda: self.aplicarColor("fondoCrono"))  #  cambia color fondo crono
        self.pushButton_rutaGUI.clicked.connect(self.rutaGUI) # llamar para seleccionar una ruta gui personalizable
        self.pushButton_restaurarConfig.clicked.connect(self.restaurar) # restaura todos los valores por defecto
        self.pushButton_restaurarRuta.clicked.connect(self.restaurar_ruta)  # restaura solo ruta

    # aplica los valores de configuracion almacenados
    def cargar_configuracion(self):
        self.configData = config.leer_configuracion()
        self.lang = self.configData["general"]["languaje"]  # leer configuracion y crear var contenedora

        self.lineEdit_testCrono.setFont(self.fuente_para_cargar("font_crono"))
        self.lineEdit_testEvent.setFont(self.fuente_para_cargar("font_evento"))
        self.lineEdit_testAlarm.setFont(self.fuente_para_cargar("font_alarma"))
        self.lineEdit_testCrono.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {self.configData["color_crono"]["fondo"]};
                    color: {self.configData["color_crono"]["texto"]};
                    border: 1px solid #555;
                    padding: 5px;
                }}
            """)
        self.lineEdit_rutaGUI.setText(f'{self.configData["general"]["gui_path"]}')


    # fuente a carga
    def fuente_para_cargar(self,item):
        font = QFont()
        font.setFamily(self.configData[item]["family"])
        font.setPointSize(self.configData[item]["point_size"])
        font.setWeight(self.configData[item]["weight"])
        font.setItalic(self.configData[item]["italic"])
        font.setUnderline(self.configData[item]["underline"])
        font.setStrikeOut(self.configData[item]["strikeout"])
        font.setBold(self.configData[item]["bold"])
        return  font


    # CARGAR el idioma de la ventana
    def cargar_idioma(self,idioma):
        # idioma = spanish
        self.lang = idioma
        self.current_language = idioma  # idioma por defecto
        self.ui = "ui_config"  # nombre del JSON UI para la ventana edit_event
        self.message = "messages_config"  # nombre del JSON mensaje
        translation_manager.set_language(self.current_language)  # actualizar idioma seleccionado
        translation_manager.set_name_ui(self.ui, self.message)
        self.update_texts()  # actualiza el texto del idioma seleccionado
        # -------------
        # nota poner en todas las ventanas que tiene avisos
        # ventana de aviso recarga al cambiar idioma por terceras apps
        self.title_1 = translation_manager.get_message("titulo 1")
        self.title_2 = translation_manager.get_message("titulo 2")
        self.content_2 = translation_manager.get_message("contenido 2")
        self.title_3 = translation_manager.get_message("titulo 3")
        self.content_3 = translation_manager.get_message("contenido 3")



    #----------------------------------------------------
    # # abrir ventana de FONDO DE TEXTO para cargar cambio de fuente
    def openFontDialog(self, item):
        estado = False # indica si ha sido seleccionado una nueva fuente
        # Crear el diálogo como objeto
        font_dialog = QFontDialog(self)
        # se lee la fuente usada para cada prueba
        if item == "crono":
            font_dialog.setCurrentFont(self.lineEdit_testCrono.font())
        if item == "evento":
            font_dialog.setCurrentFont(self.lineEdit_testEvent.font())
        if item == "alarma":
            font_dialog.setCurrentFont(self.lineEdit_testAlarm.font())

        font_dialog.setWindowTitle("Seleccionar Fuente") # titulo de la ventana

        # Mostrar el resultado del diálogo
        if font_dialog.exec():
            estado = True
            selected_font = font_dialog.selectedFont()
            # Crear diccionario con la configuración de la fuente
            font_config = {
                "family": selected_font.family(),
                "point_size": selected_font.pointSize(),
                "weight": selected_font.weight(),
                "italic": selected_font.italic(),
                "underline": selected_font.underline(),
                "strikeout": selected_font.strikeOut(),
                "bold": selected_font.bold()
            }

            # Añadir la configuración a la lista
            self.font_configs = font_config
            print(self.font_configs)
        return estado

    # metodo para aplicar cambio
    def aplicarFondo(self, item):

        if self.openFontDialog(item):
            print("leer fondo actual")
            # poner fuente seleccionada
            # Crear un objeto QFont con la configuración
            font = QFont()
            font.setFamily(self.font_configs["family"])
            font.setPointSize(self.font_configs["point_size"])
            font.setWeight(self.font_configs["weight"])
            font.setItalic(self.font_configs["italic"])
            font.setUnderline(self.font_configs["underline"])
            font.setStrikeOut(self.font_configs["strikeout"])
            font.setBold(self.font_configs["bold"])

            # Aplicar la fuente al widget correcto en test y asignar var para almacenar
            if item == "crono":
                self.lineEdit_testCrono.setFont(font)
                self.font_Crono = self.font_configs
                self.configData["font_crono"] = self.font_Crono # asignar fuente crono


            if item == "evento":
                self.lineEdit_testEvent.setFont(font)
                self.font_Event = self.font_configs
                self.configData["font_evento"] = self.font_Event  # asignar fuente evento

            if item == "alarma":
                self.lineEdit_testAlarm.setFont(font)
                self.font_Alarm = self.font_configs
                self.configData["font_alarma"] =  self.font_Alarm  # asignar fuente alarma

    # ------------------------------------------------------------------

    # Aplicar el color del texto o el fondo para los numeros de crono
    def aplicarColor(self, elemento):
        # Abre el diálogo de selección de color
        color = QColorDialog.getColor()
        if color.isValid():
            if elemento == "textoCrono":
                print(f"Color textoCrono: {color.name()}")
                self.colorTexto = color.name()
                self.configData["color_crono"]["texto"] = f"{self.colorTexto}"
            if elemento == "fondoCrono":
                print(f"Color fondoCrono: {color.name()}")
                self.colorFondo = color.name()
                self.configData["color_crono"]["fondo"] = f"{self.colorFondo}"

        # poner color texto y fondo en LineEdit
        self.lineEdit_testCrono.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.colorFondo};
                color: {self.colorTexto};
                border: 1px solid #555;
                padding: 5px;
            }}
        """)

    # poner ruta gui para la pantalla de crono
    def rutaGUI(self):
        directorio_busqueda = rutas.RUTA_GUI # ruta para buscar gui extras
        directory = QFileDialog.getExistingDirectory(
            self,
            self.title_1,
            directorio_busqueda,  # Directorio inicial
            QFileDialog.Option.ShowDirsOnly
        )
        if directory:
            self.lineEdit_rutaGUI.setText(f'{directory}') # poner ruta en lineEdit
            self.configData["general"]["gui_path"] = f"{directory}"

    # accion de combobox cambio
    def seleccion_idioma(self):
        self.lang = self.comboBox_idioma.currentText()
        indice_seleccionado = self.comboBox_idioma.currentIndex()
        print(f"seleccion Idioma: {self.lang} {indice_seleccionado} ")

        self.configData["general"]["languaje"] = f"{self.lang}"  # el nuevo idioma
        self.cargar_idioma(self.lang)  # CARGAR el idioma de la ventana


        # aplicar cambio de idioma a todas las ventanas
        if not self.main_window is None:
            self.main_window.actualizar_idioma(self.lang)  # actualizar idima en el en clase MainWindow_Cronometro

    # idioma de la ventana actualiza
    def update_texts(self):
        self.setWindowTitle(translation_manager.get_ui_text("window_title"))
        self.label_2.setText(translation_manager.get_ui_text("label_2"))
        self.pushButton_cerrar.setText(translation_manager.get_ui_text("pushButton_cerrar"))
        self.pushButton_guardar.setText(translation_manager.get_ui_text("pushButton_guardar"))
        # nuevos widgets 28122025
        self.label_1.setText(translation_manager.get_ui_text("label_1"))
        self.label.setText(translation_manager.get_ui_text("label"))
        self.pushButton_fontCrono.setText(translation_manager.get_ui_text("pushButton_fontCrono"))
        self.label_7.setText(translation_manager.get_ui_text("label_7"))
        self.pushButton_colorTexto.setText(translation_manager.get_ui_text("pushButton_colorTexto"))
        self.pushButton_colorFondo.setText(translation_manager.get_ui_text("pushButton_colorFondo"))
        self.label_6.setText(translation_manager.get_ui_text("label_6"))
        self.label_11.setText(translation_manager.get_ui_text("label_11"))
        self.pushButton_fontEvent.setText(translation_manager.get_ui_text("pushButton_fontEvent"))
        self.label_8.setText(translation_manager.get_ui_text("label_8"))
        self.label_12.setText(translation_manager.get_ui_text("label_12"))
        self.pushButton_fontAlarm.setText(translation_manager.get_ui_text("pushButton_fontAlarm"))
        self.label_9.setText(translation_manager.get_ui_text("label_9"))
        self.pushButton_rutaGUI.setText(translation_manager.get_ui_text("pushButton_rutaGUI"))
        self.pushButton_restaurarRuta.setText(translation_manager.get_ui_text("pushButton_restaurarRuta"))
        self.label_3.setText(translation_manager.get_ui_text("label_3"))
        self.pushButton_restaurarConfig.setText(translation_manager.get_ui_text("pushButton_restaurarConfig"))

        # idiomas disponibles desde combobox
        self.comboBox_idioma.clear()
        self.comboBox_idioma.addItems(translation_manager.listado_idiomas())

        # buscar idioma usado para seleccionar en combobox
        indice = translation_manager.listado_idiomas().index(self.lang)
        self.comboBox_idioma.setCurrentIndex(indice)  # Selecciona el t
        print(f"Indice deL IDIOMA {indice}")  # Output: 1
        print(translation_manager.listado_idiomas())

    # guardar
    def guardar(self):
        print("btn guardar config")

        # se actualiza para< grabar el path gui en caso de modificacion por teclado
        self.configData["general"]["gui_path"] = self.lineEdit_rutaGUI.text()
        config.guardar_configuracion(self.configData) # guardar datos
        title = translation_manager.get_message("titulo 2")
        content = translation_manager.get_message("contenido 2")
        QMessageBox.information(
            self,
            self.title_2,
            self.content_2
        )

    # restaura a valores por defecto
    def restaurar(self):
        config.guardar_configuracion(config.configuracion_inicial())  # guardar con valores iniciales datos
        QMessageBox.information(
            self,
            self.title_3,
            self.content_3
        )


    # restaurar solo ruta
    def restaurar_ruta(self):
        self.lineEdit_rutaGUI.setText("gui")  # poner ruta por defecto


    def closeEvent(self, event: QCloseEvent):
        """Maneja el evento de cierre de la ventana"""
        print("⚠️  ventana Ayuda cerrando...")
        event.accept()

# ---------------------------------------------
# Solo ejecuta si es el archivo principal
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = EditConfig_class(None, "spanish")

    app.exec()
