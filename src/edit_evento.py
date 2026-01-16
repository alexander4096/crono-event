# esta clase se comunica con la clase main_window para actualizar
#  el submenu de evento al modificar el listado
from datetime import datetime
import sys
import json
import os # uso de rutas y sistema de archivo
from PyQt6 import QtWidgets
from PyQt6 import uic
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette, QColor, QFont, QAction
from PyQt6.QtWidgets import QMessageBox, QColorDialog, QListWidget, QMenu, QApplication
import ruta_archivo_linux as datafile # path and files para guardar datos de usuario en linux
from translations import translation_manager # manejador de idiomas

class EditarEvento_class(QtWidgets.QDialog):
    def __init__(self,  main_window, idioma):
        super().__init__()
        self.main_window = main_window  # Guarda la referencia a la instancia de A

        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint) # poner al frente
        # cargar GUI
        # 1. Obtiene la ruta absoluta de la carpeta donde está este archivo (src/)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # 2. Construye la ruta subiendo un nivel y entrando a /gui
        # '..' significa "subir una carpeta"
        path_ui = os.path.join(BASE_DIR, "gui", "edit_evento.ui")

        # 3. Carga la interfaz
        if os.path.exists(path_ui):
            uic.loadUi(path_ui, self)
        else:
            print(f"Error: No se encontró el archivo UI en: {path_ui}")


        self.show()

        # CARGAR el idioma de la ventana
        self.cargar_idioma(idioma)

        # Establece el título de la ventana
        self.lineEdit_tiempo.setInputMask("00:00:00;") # mascara en QLineEdit para entrada de datos
        self.lineEdit_tiempo.setText("00:00:00")        # valor inicial


        # inicializar variables
        self.ruta = datafile.events_dir  # ruta por defecto para guardar los evento
        self.archivo = ""     # nombre del archivo de evento
        self.archivos = []    # listado contenedor de archivos eventos
        self.hh_int = 0
        self.mm_int = 0
        self.ss_int = 0
        # Lista de diccionarios de actividad (estructura)
        self.tiempo_evento = []
        self.index_tiempo_evento = 0
        """
        self.tiempo_evento = [{"actividad": "00:00:35", "tema": "uno", "bg": "#ffffff"},
                              {"actividad": "00:00:15", "tema": "dos", "bg": "#ffffff"},
                              {"actividad": "00:00:45", "tema": "tres", "bg": "#ffffff"}]
        """
        self.color_fondo = "#ffffff" # colo de fondo inicial
        # Cargar listado Combobox Eventos
        self.comboBox_eventos.clear()  # limpiar todo listado de combobox
        self.cargar_combobox_eventos()          # carga combobox
        self.comboBox_eventos.clearEditText()   # limpia el campo editable del Qcombobox

        # Configurar menú contextual
        self.setup_context_menu()

        # Eventos de botones
        self.pushButton_nuevo.clicked.connect(self.nuevo)                           # nuevo evento
        self.pushButton_guardar.clicked.connect(self.guardar)                       # guardar evento
        self.pushButton_eliminar.clicked.connect(self.eliminar)                     # eliminar evento
        self.pushButton_quitar.clicked.connect(self.quitar)                         # btn quitar actividad
        self.pushButton_agregar.clicked.connect(self.agregar)                       # btn agregar actividad
        self.pushButton_poner_color.clicked.connect(self.poner_color)               # btn poner color de fondo
        self.listWidget_lista_actividad.clicked.connect(self.selector_lista)        # selecciona item de lista
        self.comboBox_eventos.activated.connect(self.seleccion_eventos)   # seleccion eventos en combobox activated. permite elegir desde 1 index pero se debe validar


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
        time_str = self.lineEdit_tiempo.text()
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
        self.lineEdit_tiempo.setText(f"{self.hh_int:02d}:{self.mm_int:02d}:{self.ss_int:02d}")





    # BLOQUE de MENU CONTEXTUAL para copia contenido QlistWidget a la papelera
    def setup_context_menu(self):
        """Configura el menú contextual para todos los QListWidget"""
        # Si tienes varios listWidget, puedes hacerlo en un bucle
        list_widgets = self.findChildren(QListWidget)

        for list_widget in list_widgets:
            list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            list_widget.customContextMenuRequested.connect(
                lambda pos, lw=list_widget: self.on_list_context_menu(pos, lw)
            )

    def on_list_context_menu(self, position, list_widget):
        """Muestra menú contextual para un QListWidget específico"""
        if list_widget.count() == 0:
            return

        menu = QMenu()
        # Acción para copiar todo
        copy_all = QAction(self.qmenu_linea_1, self)
        copy_all.triggered.connect(
            lambda checked, lw=list_widget: self.copy_all_from_list(lw)
        )
        menu.addAction(copy_all)

        # Solo mostrar "Copiar selección" si hay elementos seleccionados
        if list_widget.selectedItems():
            copy_selected = QAction(self.qmenu_linea_2, self)
            copy_selected.triggered.connect(
                lambda checked, lw=list_widget: self.copy_selected_from_list(lw)
            )
            menu.addAction(copy_selected)

        menu.exec(list_widget.viewport().mapToGlobal(position))

    def copy_all_from_list(self, list_widget):
        """Copia todo el contenido de un QListWidget"""
        items_text = [list_widget.item(i).text() for i in range(list_widget.count())]
        text_to_copy = "\n".join(items_text)

        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)

        # Opcional: Mostrar notificación
        self.show_message(f"Copiados {len(items_text)} elementos")

    def copy_selected_from_list(self, list_widget):
        """Copia los elementos seleccionados"""
        selected_text = [item.text() for item in list_widget.selectedItems()]
        text_to_copy = "\n".join(selected_text)

        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)

        self.show_message(f"Copiados {len(selected_text)} elementos seleccionados")

    def show_message(self, message):
        """Muestra un mensaje (puedes usar QMessageBox o una barra de estado)"""
        print(message)  # O usa QMessageBox
    # --------------------------------------------------------------

    # CARGAR el idioma de la ventana
    def cargar_idioma(self, idioma):
        self.current_language = idioma  # idioma por defecto
        self.ui = "ui_edit_event"  # nombre del JSON UI para la ventana edit_event
        self.message = "messages_edit_event"  # nombre del JSON mensaje para la ventna edit_event
        translation_manager.set_language(self.current_language)  # actualizar idioma seleccionado
        translation_manager.set_name_ui(self.ui, self.message)
        self.update_texts()  # actualiza el texto del idioma seleccionado

        # nota poner en todas las ventanas que tiene avisos
        # ventana de aviso recarga al cambiar idioma por terceras apps
        self.qmenu_linea_1 = translation_manager.get_ui_text("qmenu_linea_1")
        self.qmenu_linea_2 = translation_manager.get_ui_text("qmenu_linea_2")

    # idioma de la ventana actualiza
    def update_texts(self):
        self.setWindowTitle(translation_manager.get_ui_text("window_title"))
        self.label_1.setText(translation_manager.get_ui_text("label_1"))
        self.label_2.setText(translation_manager.get_ui_text("label_2"))
        self.label_3.setText(translation_manager.get_ui_text("label_3"))
        self.label_4.setText(translation_manager.get_ui_text("label_4"))
        self.pushButton_agregar.setText(translation_manager.get_ui_text("pushButton_agregar"))
        self.pushButton_eliminar.setText(translation_manager.get_ui_text("pushButton_eliminar"))
        self.pushButton_guardar.setText(translation_manager.get_ui_text("pushButton_guardar"))
        self.pushButton_nuevo.setText(translation_manager.get_ui_text("pushButton_nuevo"))
        self.pushButton_poner_color.setText(translation_manager.get_ui_text("pushButton_poner_color"))
        self.pushButton_quitar.setText(translation_manager.get_ui_text("pushButton_quitar"))


    # seleccion del combobox de los evento guardados
    def seleccion_eventos(self, indice):
        print("seleccionar evento")
        if indice > -1: # solo carga si el indice ha sido seleccionado
            self.archivo = self.comboBox_eventos.itemText(indice)
            print(f"Selección actual: {indice} = {self.archivo}")
            try:
                self.tiempo_evento = []                  # limpia listado de actividades
                self.listWidget_lista_actividad.clear()  # limpia widget listado de actividades

                self.ruta_archivo = os.path.join(self.ruta, self.archivo)
                # Leer el archivo y convertirlo de nuevo en una lista
                with open(self.ruta_archivo, "r") as archivo:
                    listado = json.load(archivo)

                self.tiempo_evento = listado
                # ordenar y mostrar contenido
                self.actualizar_listado()  # actualiza el listado y ordenar

            except json.JSONDecodeError as e:
                print(f"Error json al leer archivo: {e}")
                title = translation_manager.get_message("Error 1")
                content = translation_manager.get_message("contenido 1")
                QMessageBox.warning(
                    self,
                    title,
                    content
                )
            except Exception as e:
                print(f"Error general archivo: {e}")
                title = translation_manager.get_message("Error 2")
                content = translation_manager.get_message("contenido 2")
                QMessageBox.warning(
                    self,
                    title,
                    content
                )


    # seleccionar item en lista
    def selector_lista(self):
        index = self.listWidget_lista_actividad.currentRow()  # fila seleccionada
        print(f"seleccionar item = {index}")

        # colocar item en campos editables
        self.lineEdit_tiempo.setText(self.tiempo_evento[index]["actividad"])  # QLineEdit tiempo
        self.lineEdit_actividad.setText(self.tiempo_evento[index]["tema"])  # QLineEdit actividad
        # poner color de fondo en QLineEdit
        self.color_fondo = self.tiempo_evento[index]["bg"]
        palette = self.lineEdit_ver_color.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(self.color_fondo))
        self.lineEdit_ver_color.setPalette(palette)


    # carga el cajon para seleccionar un color
    def poner_color(self):
        # Abre el diálogo de selección de color
        color = QColorDialog.getColor()
        if color.isValid():
            print(f"Color seleccionado: {color.name()}")

        # poner color de fondo en QLineEdit
        self.color_fondo = f"{color.name()}"
        palette = self.lineEdit_ver_color.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(self.color_fondo))
        self.lineEdit_ver_color.setPalette(palette)

    # agregar actividad al evento
    def agregar(self):
        salida = self.validacion() # ejecutar validacion
        if  salida == "ok":
            print("agregar")
            # almacer actividad  en listado
            # inicializar variables
            hora_formateada = f"{self.hh_int:02d}:{self.mm_int:02d}:{self.ss_int:02d}"
            print(hora_formateada)  # Salida de tiempo en : 00:01:01

            # agregar contenido a variable listado
            self.tiempo_evento.append({"actividad": hora_formateada,
                                       "tema": f"{self.lineEdit_actividad.text()}",
                                       "bg": f"{self.color_fondo}"})
            print(self.tiempo_evento)
            # ordenar y mostrar contenido
            self.actualizar_listado()       # actualiza el listado y ordenar
            self.limpiar_barra_actividad()  # metodo limpia barra de actividad

        elif salida == "modificar":
            print("modificar")
            hora_formateada = f"{self.hh_int:02d}:{self.mm_int:02d}:{self.ss_int:02d}"
            print(hora_formateada)  # Salida de tiempo en : 00:01:01

            # agregar contenido a variable listado
            self.tiempo_evento[self.index_tiempo_evento]["actividad"] = hora_formateada
            self.tiempo_evento[self.index_tiempo_evento]["tema"] = self.lineEdit_actividad.text()
            self.tiempo_evento[self.index_tiempo_evento]["bg"] = self.color_fondo

            print(self.tiempo_evento)
            # ordenar y mostrar contenido
            self.actualizar_listado()       # actualiza el listado y ordenar
            self.limpiar_barra_actividad()  # metodo limpia barra de actividad





    # ordena y actualiza contenido del QListWidget
    def actualizar_listado(self):

        # Ordenar por el campo "actividad" en orden ascendente
        self.tiempo_evento = sorted(
            self.tiempo_evento,
            key=lambda x: datetime.strptime(x["actividad"], "%H:%M:%S")
        )

        self.listWidget_lista_actividad.clear()  # limpia widget listado de actividades

        # poner datos en widget listbox usar una fuente proporcional para tabulacion
        font = QFont("Monospace", 9)
        self.listWidget_lista_actividad.setFont(font)

        for evento in self.tiempo_evento:
            tiempo = evento['actividad'].ljust(10)
            tema = self.truncar_texto(evento['tema'], 50).ljust(55)  # Truncar a 45 chars
            bg = evento['bg']
            # cadena formateada con tabulacion
            formateado = f"{tiempo} | {tema} | BG={bg}"
            self.listWidget_lista_actividad.addItem(formateado)

    # truncar texto de tema si pasa mas de 55 chars
    def truncar_texto(self, texto, max_caracteres):
        if len(texto) > max_caracteres:
            return texto[:max_caracteres - 3] + "..."
        return texto

    # limpiar combobox para crear un archivo de evento
    def nuevo(self):
        print("nuevo")
        self.comboBox_eventos.clearEditText()  # limpia el campo editable del Qcombobox
        self.listWidget_lista_actividad.clear() # limpiar QlistWidget
        self.limpiar_barra_actividad() # metodo limpia barra de actividad
        self.tiempo_evento.clear() # limpia listado de actividades

    def limpiar_barra_actividad(self):
        self.lineEdit_tiempo.setText("00:00:00")
        self.lineEdit_actividad.setText("")  # limpiar QLineEdit actividad
        # poner color de fondo en QLineEdit
        self.color_fondo = "#ffffff"
        palette = self.lineEdit_ver_color.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(self.color_fondo))
        self.lineEdit_ver_color.setPalette(palette)


    # guardar actividades en archivo de eventos
    def guardar(self):
        print("guardar")
        try:
            self.archivo = self.comboBox_eventos.currentText() # toma el texto del campo editable combobox
            self.ruta_archivo = os.path.join(self.ruta, self.archivo)
            # Guardar el listado en formato JSON en el archivo indent= 4 (permite sangrias)

            print(f" datos a guardar: {self.tiempo_evento}")

            with open(self.ruta_archivo, "w") as archivo:
                json.dump(self.tiempo_evento, archivo, indent=4)

            # Buscar el índice del ítem
            item_buscar = self.archivo
            self.cargar_combobox_eventos()  # carga combobox

            if not  self.main_window is None: # si existe clase main_window ejecuta el metodo
                self.main_window.actualizar_submenu() # actualizar submenu de cronometro en clase MainWindow_Cronometro

            try:
                indice = self.archivos.index(item_buscar)
                self.comboBox_eventos.setCurrentIndex(indice)
                print(f"El índice de '{item_buscar}' es: {indice}")
            except ValueError:
                print(f"El ítem '{item_buscar}' no está en la lista.")

            title = translation_manager.get_message("title 1")
            content = translation_manager.get_message("respuesta 1")
            QMessageBox.information(
                self,
                title,
                content
            )

        except PermissionError:
            print(f"Error: No tienes permisos para escribir en la ruta '{self.ruta_archivo}'.")
            title = translation_manager.get_message("Error 3")
            content = translation_manager.get_message("contenido 3")
            QMessageBox.warning(
                self,
                title,
                content
            )
        except OSError as e:
            print(f"Error al crear la carpeta o escribir el archivo: {e}")
            title = translation_manager.get_message("Error 4")
            content = translation_manager.get_message("contenido 4")
            QMessageBox.warning(
                self,
                title,
                content
            )
        except TypeError:
            print("Error: Los datos no pueden ser convertidos a JSON. Verifica la estructura de 'self.tiempo_evento'.")
            title = translation_manager.get_message("Error 5")
            content = translation_manager.get_message("contenido 5")
            QMessageBox.warning(
                self,
                title,
                content
            )
        except Exception as e:
            print(f"Error inesperado al guardar el archivo: {e}")
            title = translation_manager.get_message("Error 6")
            content = translation_manager.get_message("contenido 6")
            QMessageBox.warning(
                self,
                title,
                content
            )


    # eliminar evento de archivo
    def eliminar(self):
        print("eliminar")
        try:
            self.ruta_archivo = os.path.join(self.ruta, self.archivo) # ruta y archivo
            os.remove(self.ruta_archivo)
            print(f"El archivo '{self.ruta_archivo}' ha sido borrado.")
            self.cargar_combobox_eventos()  # carga combobox

            if not self.main_window is None:  # si existe clase main_window ejecuta el metodo
                self.main_window.actualizar_submenu()  # actualizar submenu de cronometro en clase MainWindow_Cronometro

            title = translation_manager.get_message("title 2")
            content = translation_manager.get_message("respuesta 2")
            QMessageBox.information(
                self,
                title,
                content
            )
        except FileNotFoundError:
            print(f"Error: El archivo '{self.ruta_archivo}' no existe.")
            title = translation_manager.get_message("Error 8")
            content = translation_manager.get_message("contenido 8")
            QMessageBox.critical(
                self,
                title,
                content
            )
        except PermissionError:
            print(f"Error: No tienes permisos para borrar '{self.ruta_archivo}'.")
            title = translation_manager.get_message("Error 9")
            content = translation_manager.get_message("contenido 9")
            QMessageBox.critical(
                self,
                title,
                content
            )
        except Exception as e:
            print(f"Error inesperado: {e}")
            title = translation_manager.get_message("Error 10")
            content = translation_manager.get_message("contenido 10")
            QMessageBox.critical(
                self,
                title,
                content
            )


    # quita una actividad del evento
    def quitar(self):
        print("quitar")
        selected_item = self.listWidget_lista_actividad.currentItem()
        if selected_item:
            print("Ítem seleccionado")
            index = self.listWidget_lista_actividad.currentRow()  # fila seleccionada
            del self.tiempo_evento[index]
            # ordenar y mostrar contenido
            self.actualizar_listado()  # actualiza el listado y ordenar
            # limpiar campos de entrada
            self.lineEdit_tiempo.setText("00:00:00")  # limpiar QLineEdit tiempo
            self.lineEdit_actividad.setText("")  # limpiar QLineEdit actividad
            # poner color de fondo en QLineEdit
            self.color_fondo = "#ffffff"
            palette = self.lineEdit_ver_color.palette()
            palette.setColor(QPalette.ColorRole.Base, QColor(self.color_fondo))
            self.lineEdit_ver_color.setPalette(palette)
        else:
            print("No hay ningún ítem seleccionado.")


    # cargar QComboBox con listado de archivos eventos
    def cargar_combobox_eventos(self):
        # Ruta del subdirectorio 'eventos'
        ruta_eventos = datafile.events_dir  # Asegúrate de que esta ruta sea correcta
        if not os.path.exists(ruta_eventos):
            print(f"Error: El directorio '{ruta_eventos}' no existe.")
        elif not os.path.isdir(ruta_eventos):
            print(f"Error: '{ruta_eventos}' no es un directorio.")
        else:
            self.archivos = os.listdir(ruta_eventos)
            # Filtrar solo los archivos (excluyendo subdirectorios)
            self.archivos = [archivo for archivo in self.archivos if
                             os.path.isfile(os.path.join(ruta_eventos, archivo))]
            # Ordenar la lista alfabéticamente
            self.archivos = sorted(self.archivos)
            print("Archivos en el directorio:", self.archivos)
            self.comboBox_eventos.clear()                 # borrar listado combobox
            self.comboBox_eventos.addItems(self.archivos) # cargar listado de eventos


    # metodo de validacion de entraada en campo tiempo
    def validacion(self):
        print("validar tiempo de actividad")
        salida = "ok"
        # Obtener el texto del QLineEdit
        time_str = self.lineEdit_tiempo.text()
        print(f"captura time:{time_str} ")
        # Separar hh, mm, ss
        hh, mm, ss = time_str.split(":")

        # Validar los valores de tiempo
        self.hh_int = int(hh) if hh else 0
        self.mm_int = int(mm) if mm else 0
        self.ss_int = int(ss) if ss else 0

        # validacion cuando la hora es 00:00:00 no se ha fijado un tiempo
        if self.hh_int == 0 and self.mm_int == 0 and self.ss_int == 0 and salida == "ok":
            title = translation_manager.get_message("Error 11")
            content = translation_manager.get_message("contenido 11")
            QMessageBox.warning(
                self,
                title,
                content
            )
            salida = "fail"

        # VALIDACION PARA MODIFICIAR
        #  si ya existe el tiempo de actividad en evento (se modifica contenido)
        if salida == "ok":
            for index, tiempo in enumerate(self.tiempo_evento):
                print(f"{time_str} == {tiempo}")
                if tiempo["actividad"] == f"{self.hh_int:02d}:{self.mm_int:02d}:{self.ss_int:02d}":
                    self.index_tiempo_evento = index
                    print(f"posicion = {index}")

                    salida = "modificar"
                    break  # Rompe el ciclo una vez eliminado

        # validacion si el campo lineEdit_actividad esta vacio
        if len(self.lineEdit_actividad.text()) == 0 and salida == "ok":
            title = translation_manager.get_message("Error 12")
            content = translation_manager.get_message("contenido 12")
            QMessageBox.warning(
                self,
                title,
                content
            )
            salida = "fail"

        return salida



# ---------------------------------------------
# Solo ejecuta si es el archivo principal
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = EditarEvento_class(None, "english")
    app.exec()
