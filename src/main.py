"""
 * Nombre del Programa: crono-event
 * Descripción:  This program is a timer for events and activities that allows you to set the time and set alarms.
 * * Fecha de desarrollo: 15/01/2026
 * Programador: Alexander Rodriguez
 * Email: alexander1973r@gmail.com
 * Versión: 1.0.0
 *
 * Copyright (C) 2026 Alexander Rodriguez
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details. [cite: 158, 159, 160]
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>. [cite: 161, 162]
 """
import sys
import os
import json # lectura y escritura en formato json
import datetime
from functools import partial # pasar parametros en llamadas a metodos por los eventos
from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer, Qt, QUrl  # tiempo en el widget
from PyQt6 import uic                   # cargar uic windows
from PyQt6.QtGui import QCloseEvent, QPalette, QColor, QAction, QIcon, QFont  # cerrar por evento, paleta colores
from PyQt6.QtCore import Qt             # Importa Qt para usar WindowStaysOnTopHint
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtWidgets import QPushButton, QMessageBox, QLineEdit  # btn cambiar color de fondo
# importacion de librarias personales
from edit_evento import EditarEvento_class          # ventana EditarEventos
from edit_crono  import EditarCrono_class           # ventana EditarCrono
from edit_alarma import EditarAlarma_class          # ventana EditarAlarma_class
from edit_config import EditConfig_class            # ventana EditarConfig_class
from historico_pausa import HistoricoPausa_class    # ventana historico de pausa
from acerca import Acerca_class                     # ventana Acerca
from ayuda  import  Ayuda_class                     # ventana Ayuda
from licencia import Licencia_class                 # ventana de licencia
from ver_evento import VerEvento_class              # ventana VerEvento_class
from ver_alarma import VerAlarma_class              # ventana VerAlarma_class
import configuracion as config                      # lee y escribe configuracion del programa
import ruta_archivo_linux as datafile               # ruta de archivos para guardar datos de usuario en linux
from translations import translation_manager        # manejador de idiomas subcarpeta name

# ------------------------------
# clase ventana Principal
# ------------------------------
class MainWindow_Cronometro(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # Configurar la ventana para que siempre esté en primer plano
        # debe estar antes de ser mostrada
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # LEER configuracion
        self.configData = None
        self.correr_configuracion()

        # cargar GUI
        try:

            # 1. Obtiene la ruta absoluta de la carpeta donde está este archivo (src/)
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))

            # 2. Construye la ruta subiendo un nivel y entrando a /gui
            # '..' significa "subir una carpeta"
            path_ui = os.path.join(BASE_DIR,  self.configData["general"]["gui_path"], "cronometro.ui")

            # 3. Carga la interfaz
            if os.path.exists(path_ui):
                uic.loadUi(path_ui, self)
            else:
                print(f"Error: No se encontró el archivo UI en: {path_ui}")


            self.show()

            # APLICAR configuracion en widgets  QLineEdit para ventana Crono
            self.lineEdit_hora.setFont(self.fuente_para_cargar("font_crono"))  # config display timer
            self.lineEdit_hora.setStyleSheet(f"""
                                  QLineEdit {{
                                      background-color: {self.configData["color_crono"]["fondo"]};
                                      color: {self.configData["color_crono"]["texto"]};
                                      border: 1px solid #555;
                                      padding: 5px;
                                  }}
                              """)
            # ------------------------------------

            # sonido
            self.sound_effect = QSoundEffect()  # cargar reproducto de audio
            self.selected_file = ""
            self.wav_dir = "wav"  # Subdirectorio donde están los archivos .wav
            self.volume = 0.8  # valor del volumen 0.0 a 1.0
            self.repeat_sound = 10  # veces que repite el sonido

            self.titulo_modo = None  # aviso de modos inicializacion (se almacena los modos)
            self.estado_actionAlarma = None  # estado de alarma

            # CARGAR el idioma de la ventana
            self.cargar_idioma(self.lang)
            icon= os.path.join("icons", "alarm-clock_icon_128x128.png") # ruta de icono
            self.setWindowIcon(QIcon(icon))  # Establece el icono de la ventana
            self.timer = QTimer()  # tiempo
            self.timer.timeout.connect(lambda: self.update(True))
            self.timer.start(1000)  # 1000 milisegundos = 1 segundo

            # obtener el color del boton por defecto
            palette = self.pushButton_iniciar.palette()
            # Obtener el color de fondo (background) del botón
            background_color = palette.color(QPalette.ColorRole.Button)
            # Obtener los componentes RGB
            rojo = background_color.red()
            verde = background_color.green()
            azul = background_color.blue()
            self.bgColor_default = (rojo, verde, azul)
            self.bgColor_active = (70, 255, 0)  # (255, 162, 0)
            # Variable para almacenar la referencia a la ventana secundarias
            self.ventanas = [None, None, None, None, None, None, None, None, None, None,
                             None]  # var para indicar cual ventana esta abierta
            """
                  listado de ventanas auxiliares
                  parametro usado en metodo self.abrir_ventana(n)
                  0 = (SIN USO)
                  1 = editar chronometro
                  2 = acerca
                  3 = ayuda
                  4 = editar evento
                  5 = (configuracion)
                  6 = registro de pausas
                  7 = editar alarma
                  8 = ver evento
                  9 = ver alarma
                  10 = ver Licencia
            """

            # INICIALIZACION de Variables
            # progresivo #aaff7f (verde)
            # regresivo  #ffff00 (amarillo)
            # hora       #ffffff (blanco)
            # evento     #ffe4c6 (marron)
            self.intermitente = False  # estado del fondo color para INDICADOR DE PAUSA
            self.intermitente_fondo_alarma = True  # estado de fondo intermentente ventana ver alarma
            self.color_fondo_reporte = ["#aaff7f", "#ffff00", "#ffe4c6", "#ffffff"]
            self.formateado = "00:00:00"  # valor inicial para cada display de tiempo

            self.memoria_pausa = []       # memoria en pausa del tiempo cronometros
            self.memoria_pausa_info = []  # memoria en pausa para descripcion del tiempo
            self.tiempo_alarma = []  # Lista de tiempos alarmas
            self.activar_alarma = "off"  # estado de la alarma
            # poner modo por defecto (progresivo)
            self.actionCronometro_Progresivo.setCheckable(True)  # Permitir que la acción sea marcable
            self.actionCronometro_Progresivo.setChecked(True)
            self.lineEdit_reporte.setText(self.titulo_modo[0])
            self.lineEdit_extra.setText("")  # limpiar pasos en evento
            self.fondo_lineEdit_porte(0)  # cambiar color de lineEdit_reporte
            self.ver_modo = 0  # modo iniciar por defecto (progresivo)
            # -------

            """
            modos (opciones de cronometro)
                0 = progresivo
                1 = regresivo
                2 = eventos
                3 = hora
            """
            self.salida_formateada = ["00:00:00", "00:00:00", "00:00:00",
                                      "00:00:00"]  # marcador de tiempo de salida para cada cronometro
            self.tiempo_en_pausa = ["00:00:00", "00:00:00", "00:00:00",
                                    "00:00:00"]  # es el tiempo entre la pausa ejecutandose
            self.iniciar_modo = ["stop", "stop", "stop", "start"]  # modos start / stop / pause
            self.cambiar_color_btn()

            self.tiempo_progresivo = [
                {
                    "hora": 0,
                    "minuto": 0,
                    "segundo": 0,
                    "pausa": ""  # screen shot tiempo antes de la pausa
                }
            ]

            self.tiempo_regresivo = [
                {
                    "hora": 0,
                    "minuto": 0,
                    "segundo": 0,
                    "pausa": ""  # screen shot del tiempo pausado
                }
            ]

            self.tiempo_evento = [
                {
                    "hora": 0,
                    "minuto": 0,
                    "segundo": 0,
                    "pausa": ""  # screen shot del tiempo pausado
                }
            ]

            self.tiempo_hora = [
                {
                    "pausa": ""  # screen shot del tiempo pausado
                }
            ]

            # activar checkbox para submenu MODO
            self.actionCronometro_Progresivo.setCheckable(True)  # Permitir que la acción sea marcable
            self.actionCrono_Regresivo.setCheckable(True)  # Permitir que la acción sea marcable
            self.actionEvento.setCheckable(True)  # Permitir que la acción sea marcable
            self.actionHora.setCheckable(True)  # Permitir que la acción sea marcable

            # eventos submenu MODO
            self.actionCronometro_Progresivo.triggered.connect(self.progresiva)  # menu progresivo
            self.actionCrono_Regresivo.triggered.connect(self.regresiva)  # menu regresivo
            self.actionHora.triggered.connect(self.hora)  # menu hora
            self.actionAlarma.triggered.connect(self.alarma)  # menu alarma
            self.actionEvento.triggered.connect(self.evento)  # menu evento
            self.actionEditar_Evento.triggered.connect(lambda: self.abrir_ventana(4))  # ventana editar evento
            self.actionConfiguracion_1.triggered.connect(lambda: self.abrir_ventana(5))  # ventana configuracion
            self.actionReg_Pausas.triggered.connect(lambda: self.abrir_ventana(6))  # ventana reg pausas
            self.actionAlarma.triggered.connect(lambda: self.abrir_ventana(7))  # ventana Alarma
            self.actionSalida.triggered.connect(self.salida)  # salida
            # evento submenu ACCION
            self.actionEditar.triggered.connect(lambda: self.abrir_ventana(1))  # ventana editar cronometro
            # evento submenu acerca
            self.actionAcerca.triggered.connect(lambda: self.abrir_ventana(2))  # ventana acerca
            self.actionAyuda.triggered.connect(lambda: self.abrir_ventana(3))  # ventana ayuda
            self.actionLicencia.triggered.connect(lambda: self.abrir_ventana(10))  # ventana licencia
            # evento submenu Borrar
            self.actionBorrar_Todo.triggered.connect(self.menu_borrar_todo)
            self.actionBorrar_Solo_Crono_Progresivo.triggered.connect(self.menu_borrar_solo_progresivo)
            self.actionBorrar_Solo_Crono_Regresivo.triggered.connect(self.menu_borrar_solo_regresivo)
            self.actionBorrar_solo_Crono_Evento.triggered.connect(self.menu_borrar_solo_evento)
            self.actionPARAR_TODO_Crono.triggered.connect(self.menu_parar_todo)
            # eventos botones
            self.pushButton_iniciar.clicked.connect(self.iniciar)  # iniciar
            self.pushButton_pausa.clicked.connect(self.pausa)  # pausa
            self.pushButton_parar.clicked.connect(self.parar)  # parar

            # botones opcionales
            if hasattr(self, 'pushButton_borrar'):
                self.pushButton_borrar.clicked.connect(self.btn_borrar) # boton para borrar
            if hasattr(self, 'checkBox_ocultar'):
                self.checkBox_ocultar.stateChanged.connect(self.ocultar_barra_menu) # ocultar barra menu
                self.checkBox_ocultar.setChecked(True)  # activo para mostra barra y titulo de ventana

            # Agregar submenús dinámicos al menú Favoritos
            self.favorito_seleccionado = None  # Para llevar el registro del favorito seleccionado
            self.archivo_favorito = ""
            self.tiempo_actividad = []  # limpia listado de actividades
            self.agregar_submenus_favoritos(self.menuListado_de_Eventos)  # pone fav arch de eventos

            # posicion  y tamaño de la ventana crono
            self.move(int(self.configData["ventana_ppal"]["pos_xy"][0]),
                      int(self.configData["ventana_ppal"]["pos_xy"][1]))  # mover ventana a ultima posicion guardada
            self.resize(int(self.configData["ventana_ppal"]["size"][0]),
                        int(self.configData["ventana_ppal"]["size"][1]))

            self.setMinimumSize(100, 76) # fijar el valor minimo para reducir ventana
            # Después de cargar el UI
            self.lineEdit_extra.setMinimumHeight(20)  # Ajusta este valor a tu gusto
            self.lineEdit_reporte.setMinimumHeight(20)

            # Opcional: Si quieres que nunca crezcan de más
            self.lineEdit_extra.setMaximumHeight(25)
            self.lineEdit_reporte.setMaximumHeight(25)

        # ---------------------------------

        except FileNotFoundError as e:
            print(f"Error: No se encontró el archivo de interfaz \n: {e}")
            # Opcional: mostrar mensaje al usuario
            QMessageBox.critical(self, "Error", f"The interface file was not found.:")
            self.ventconfig = EditConfig_class(self)
            self.ventconfig.show()

        except Exception as e:
            print(f"Error inesperado al cargar la interfaz: {e}")
            # Opcional: mostrar mensaje genérico al usuario
            QMessageBox.critical(self, "Error", f"Error loading interface:\n{str(e)}")
            self.ventconfig = EditConfig_class(self)
            self.ventconfig.show()



    # leer configuracion y poner valores
    def correr_configuracion(self):
        self.configData = config.leer_configuracion()
        self.lang = self.configData["general"]["languaje"]  # leer configuracion y crear var contenedora
        self.pos_event = self.configData["ventana_evento"]["pos_xy"]
        self.size_event = self.configData["ventana_evento"]["size"]

    # fuente a carga
    def fuente_para_cargar(self, item):
        font = QFont()
        font.setFamily(self.configData[item]["family"])
        font.setPointSize(self.configData[item]["point_size"])
        font.setWeight(self.configData[item]["weight"])
        font.setItalic(self.configData[item]["italic"])
        font.setUnderline(self.configData[item]["underline"])
        font.setStrikeOut(self.configData[item]["strikeout"])
        font.setBold(self.configData[item]["bold"])
        return font
    # ---------------------------------------


    # actualizar (Metodo para actualizar todas las ventanas en tiempo real)
    def actualizar_idioma(self, idioma):
        self.cargar_idioma(idioma)
        print(f"cambiar idioma @@@@ {idioma}")  # si existe clase main_window ejecuta el metodo
        if not self.ventanas[1] is None:  # existe ventana Edit_crono
            self.ventanas[1].cargar_idioma(idioma)

        if not self.ventanas[3] is None:  # existe ventana ayuda
            self.ventanas[3].cargar_idioma(idioma)

        if not self.ventanas[4] is None:  # existe ventana Edit_evento
            self.ventanas[4].cargar_idioma(idioma)

        if not self.ventanas[6] is None:  # existe ventana historico_pausa
            self.ventanas[6].cargar_idioma(idioma)

        if not self.ventanas[7] is None:  # existe ventana EditarAlarma
            self.ventanas[7].cargar_idioma(idioma)


    # CARGAR el idioma de la ventana main
    def cargar_idioma(self, idioma):
        self.current_language = idioma  # idioma por defecto
        self.ui = "ui_crono"  # nombre del JSON UI para la ventana edit_event
        self.message = "messages_crono"  # nombre del JSON mensaje para la ventna edit_event
        translation_manager.set_language(self.current_language)  # actualizar idioma seleccionado
        translation_manager.set_name_ui(self.ui, self.message)
        self.update_texts()  # actualiza el texto del idioma seleccionado
        # ---------

    # idioma de la ventana actualiza
    def update_texts(self):


        # actualizacion dinamica
        # parche: este codigo es para mantener los datos de las etiquetas de idiomas al abrir otras ventanana
        self.titulo_modo = translation_manager.get_ui_text("lineEdit_reporte")     # lista de de modos para reporte
        self.estado_actionAlarma = translation_manager.get_ui_text("actionAlarma") # lista de alarma estado
        # titulo ventana
        self.setWindowTitle(translation_manager.get_ui_text("window_title"))
        # menu modo
        self.menuModo.setTitle(translation_manager.get_ui_text("menuModo"))
        self.actionAlarma.setText(translation_manager.get_ui_text("actionAlarma")[0])
        self.actionConfiguracion_1.setText(translation_manager.get_ui_text("actionConfiguracion_1"))
        self.actionCrono_Regresivo.setText(translation_manager.get_ui_text("actionCrono_Regresivo"))
        self.actionCronometro_Progresivo.setText(translation_manager.get_ui_text("actionCronometro_Progresivo"))
        self.actionEditar_Evento.setText(translation_manager.get_ui_text("actionEditar_Evento"))
        self.actionEvento.setText(translation_manager.get_ui_text("actionEvento"))
        self.actionHora.setText(translation_manager.get_ui_text("actionHora"))
        self.actionReg_Pausas.setText(translation_manager.get_ui_text("actionReg_Pausas"))
        self.actionSalida.setText(translation_manager.get_ui_text("actionSalida"))
        # menu Action
        self.menuAccion.setTitle(translation_manager.get_ui_text("menuAccion"))
        self.menuBorrar.setTitle(translation_manager.get_ui_text("menuBorrar"))
        self.actionEditar.setText(translation_manager.get_ui_text("actionEditar"))
        self.actionBorrar_Solo_Crono_Progresivo.setText(translation_manager.get_ui_text("actionBorrar_Solo_Crono_Progresivo"))
        self.actionBorrar_Solo_Crono_Regresivo.setText(translation_manager.get_ui_text("actionBorrar_Solo_Crono_Regresivo"))
        self.actionBorrar_Todo.setText(translation_manager.get_ui_text("actionBorrar_Todo"))
        self.actionBorrar_solo_Crono_Evento.setText(translation_manager.get_ui_text("actionBorrar_solo_Crono_Evento"))
        self.actionPARAR_TODO_Crono.setText(translation_manager.get_ui_text("actionPARAR_TODO_Crono"))
        # submenu Listado de eventos
        self.menuListado_de_Eventos.setTitle(translation_manager.get_ui_text("menuListado_de_Eventos"))
        # menu Acerca
        self.menuAcerca.setTitle(translation_manager.get_ui_text("menuAcerca"))
        self.actionAcerca.setText(translation_manager.get_ui_text("actionAcerca"))
        self.actionAyuda.setText(translation_manager.get_ui_text("actionAyuda"))
        self.actionLicencia.setText(translation_manager.get_ui_text("actionlicencia"))
        # botones
        self.pushButton_iniciar.setText(translation_manager.get_ui_text("pushButton_iniciar"))
        self.pushButton_pausa.setText(translation_manager.get_ui_text("pushButton_pausa"))
        self.pushButton_parar.setText(translation_manager.get_ui_text("pushButton_parar"))
        # Boton opcional
        if hasattr(self, 'pushButton_borrar'):
            self.pushButton_borrar.setText(translation_manager.get_ui_text("pushButton_borrar")) # boton para borrar

    # lo llama otra clase para actualizar el submeno del contenido fav arch event
    def actualizar_submenu(self):
        self.menuListado_de_Eventos.clear()
        self.agregar_submenus_favoritos(self.menuListado_de_Eventos)

    # cargar listado de eventos_padre)
    def agregar_submenus_favoritos(self, menu_padre):
        # Lista de favoritos de Eventos (puede ser dinámica o cargada desde un archivo)
        # Ruta del subdirectorio 'eventos'
        ruta_eventos = datafile.events_dir  # Asegúrate de que esta ruta sea correcta  # Asegúrate de que esta ruta sea correcta
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

        menu_padre.clear()  # Limpiar el menú antes de agregar nuevos elementos
        for archivo in self.archivos:
            action = QAction(archivo, self)
            action.setCheckable(True)  # Permitir que la acción sea marcable
            action.triggered.connect(lambda checked, f=archivo, a=action: self.on_favorito_seleccionado(f, a))
            menu_padre.addAction(action)

    def on_favorito_seleccionado(self, favorito, action):
        # Desmarcar el favorito previamente seleccionado
        if self.favorito_seleccionado is not None:
            self.favorito_seleccionado.setChecked(False)
        # Marcar el nuevo favorito seleccionado
        action.setChecked(True)
        self.favorito_seleccionado = action
        print(f"Favorito seleccionado: {favorito}")
        self.tiempo_actividad = []  # limpia listado de actividades
        try:
            self.archivo_favorito = favorito
            self.ruta = datafile.events_dir
            self.ruta_archivo = os.path.join(self.ruta, self.archivo_favorito)
            # Leer el archivo y convertirlo de nuevo en una lista
            with open(self.ruta_archivo, "r") as archivo:
                listado = json.load(archivo)

            self.tiempo_actividad = listado
            print(f"{self.tiempo_actividad}")
            if not self.ventanas[8] is None:  # pone el titulo de evento al seleccionar uno
                self.ventanas[8].poner_titulo_ventana(self.archivo_favorito)

        except json.JSONDecodeError as e:
            print(f"Error json al leer archivo: {e}")
            title = translation_manager.get_message("Error 1")
            content = translation_manager.get_message("contenido 1")
            QMessageBox.warning(
                self,
                title,
                content
            )



    # marcar estado de alarma cuando esta activa en submenu
    def marcar_alarma_activa(self, estado):
        if estado =="on":
            self.actionAlarma.setText(self.estado_actionAlarma[1]) # "Editar Alarma [on]"
        else:
            self.actionAlarma.setText(self.estado_actionAlarma[0]) # Editar Alarma [off]

    # intermitente en color de fondo en pausa
    def cambiar_color_lineEdit_extra(self, estado):
        # "#ffffff" BLANCO
        # "#18CD0B" vERDE
        palette = self.lineEdit_extra.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff")) # blanco
        self.lineEdit_extra.setPalette(palette)
        if estado:
            palette = self.lineEdit_extra.palette()
            palette.setColor(QPalette.ColorRole.Base, QColor("#18CD0B")) # verde
            self.lineEdit_extra.setPalette(palette)

        
    # cambiar color de boton al activarse
    def cambiar_color_btn(self):
        button = QPushButton("") # btn base
        palette_default = button.palette()
        palette_default.setColor(QPalette.ColorRole.Button, QColor(*self.bgColor_default))  # Rojo
        palette_active = button.palette()
        palette_active.setColor(QPalette.ColorRole.Button, QColor(*self.bgColor_active))  # Rojo

        # poner color por defecto en botones
        self.pushButton_iniciar.setPalette(palette_default)
        self.pushButton_iniciar.setAutoFillBackground(True)
        self.pushButton_pausa.setPalette(palette_default)
        self.pushButton_pausa.setAutoFillBackground(True)
        self.pushButton_parar.setPalette(palette_default)
        self.pushButton_parar.setAutoFillBackground(True)

        # stop / start / pause
        if self.iniciar_modo[self.ver_modo] == "start":
            self.pushButton_iniciar.setPalette(palette_active)
            self.pushButton_iniciar.setAutoFillBackground(True)

        if self.iniciar_modo[self.ver_modo] == "stop":
            self.pushButton_parar.setPalette(palette_active)
            self.pushButton_parar.setAutoFillBackground(True)

        if self.iniciar_modo[self.ver_modo] == "pause":
            self.pushButton_pausa.setPalette(palette_active)
            self.pushButton_pausa.setAutoFillBackground(True)



    def closeEvent(self, event: QCloseEvent):
        """Maneja el evento de cierre de la ventana"""
        print("⚠️  Cerrando por btn Ventana...")
        self.sound_effect.stop() # para el sonido
        self.correr_configuracion() # volver a cargar configuracion actual antes de grabar
        if not (self.ventanas[8] is None): # optener pos vent pos vent evento
            self.size_event = self.ventanas[8].optener_size_ventana()
            self.pos_event = self.ventanas[8].optener_pos_vent()
            self.configData["ventana_evento"]["pos_xy"] = self.pos_event
            self.configData["ventana_evento"]["size"] = self.size_event

        # poner nuevos valores ventana crono para grabar en config
        self.configData["general"]["languaje"] = self.lang
        self.configData["ventana_ppal"]["pos_xy"] = self.pos_ppal
        self.configData["ventana_ppal"]["size"] = self.size_ppal

        config.guardar_configuracion(self.configData)  # guardar configuracion

        # cerramos todas las ventanas abiertas al cerrar el menu ppal
        for solo_ventana in self.ventanas:
            # Cerrar la ventana secundaria si existe cuando se cierra la principal
            if solo_ventana is not None:
                solo_ventana.close()

        event.accept()

    # captura evento de movimento de ventana
    def moveEvent(self, event):
        new_pos = event.pos()  # Obtiene la nueva posición de la ventana
        print(f"Ventana movida a: ({new_pos.x()}, {new_pos.y()})")
        self.pos_ppal= [new_pos.x(), new_pos.y()] # asignar valores de pos vent ppal




    # captura evento resize window
    def resizeEvent(self, event):
        new_size = event.size()  # Get the new size of the window
        print(f"Window resized to: {new_size.width()} x {new_size.height()}")
        self.size_ppal = [new_size.width(), new_size.height()]



    # ---------------------------------------
    # REPRODUCCION DE SONIDO PARA ALARMAS
    def play_sound(self):
        self.sound_effect.stop() # para la alarma actual
        self.play_audio()        # reproduce una nueva alarma


    def play_audio(self):
        """Reproduce el archivo WAV seleccionado"""
        try:
            # Configurar QSoundEffect
            self.current_file = os.path.join(self.wav_dir, self.selected_file)
            print(f" sonar = {self.current_file} {self.selected_file}")
            self.sound_effect.setSource(QUrl.fromLocalFile(self.current_file))
            self.sound_effect.setLoopCount(self.repeat_sound)
            self.sound_effect.setVolume(self.volume)
            self.sound_effect.play()  # Reproducir

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo reproducir el archivo:\n{str(e)}")
    #----------------------------------------


    # metodo que se ejecuta en el ciclo timer
    def update(self, conteo):
        self.now = datetime.datetime.now()

        # MOSTRAR FONDO INTERMITENTE si hay algun modo en pausa
        if "pause" in self.iniciar_modo:
            if self.intermitente == False:
                self.intermitente = True
                self.cambiar_color_lineEdit_extra(self.intermitente)
            else:
                self.intermitente = False
                self.cambiar_color_lineEdit_extra(self.intermitente)
        else:
            self.intermitente = False
            self.cambiar_color_lineEdit_extra(self.intermitente)

        # -------------------------------
        # MODO Progresivo index 0 (CONTADOR PROGRESIVO)
        if self.iniciar_modo[0] != "stop" and conteo == True:
            # calcular cronometro (MODO Progresivo)
            self.tiempo_progresivo[0]["segundo"] += 1
            if self.tiempo_progresivo[0]["segundo"] == 60:
                self.tiempo_progresivo[0]["segundo"] = 0
                self.tiempo_progresivo[0]["minuto"] += 1
            if self.tiempo_progresivo[0]["minuto"] == 60:
                self.tiempo_progresivo[0]["minuto"] = 0
                self.tiempo_progresivo[0]["hora"] += 1
            if self.tiempo_progresivo[0]["hora"] == 99:
                self.tiempo_progresivo[0]["minuto"] = 0

        # mostrar salida cronometro (PROGRESIVO) 0
        if self.ver_modo == 0:
            hora = self.tiempo_progresivo[0]["hora"]
            minuto = self.tiempo_progresivo[0]["minuto"]
            segundo = self.tiempo_progresivo[0]["segundo"]
            # PONER VALOR de tiempo en pausa  0 = progresivo
            if self.iniciar_modo[0] == "pause":
                self.salida_formateada[0] = self.tiempo_progresivo[0]["pause"] # poner tiempo pausado
                self.tiempo_en_pausa[0] = f"{hora:02d}:{minuto:02d}:{segundo:02d}"
                self.lineEdit_extra.setText(f"P {self.tiempo_en_pausa[0]}")  # info extra
            else:
                # almacena valor progresivo en pausa
                self.salida_formateada[0]  = f"{hora:02d}:{minuto:02d}:{segundo:02d}"
                self.tiempo_progresivo[0]["pause"] = self.salida_formateada[0]  # carga el tiempo pausado

            self.lineEdit_hora.setText(self.salida_formateada[0])  # PONER tiempo progresivo en display principal


        # --------------------------------------------------


        # MODO Regresivo valor 1 (CONTADOR REGRESIVO)
        if self.iniciar_modo[1] != "stop" and conteo == True:
            # calculo cronometro ( MODO Regresivo)
            if (self.tiempo_regresivo[0]["hora"] == 0 and
                    self.tiempo_regresivo[0]["minuto"] == 0 and
                    self.tiempo_regresivo[0]["segundo"] == 0):
                self.tiempo_regresivo[0]["hora"] = 100

            if self.tiempo_regresivo[0]["segundo"] == 0:
                self.tiempo_regresivo[0]["segundo"] = 60
                if self.tiempo_regresivo[0]["minuto"] == 0:
                    self.tiempo_regresivo[0]["minuto"] = 60
                    self.tiempo_regresivo[0]["hora"] -= 1

                self.tiempo_regresivo[0]["minuto"] -=1 # resta un minuto

            self.tiempo_regresivo[0]["segundo"] -= 1 # resta un segundo
        # mostrar salida cronometro (REGRESIVO)
        if  self.ver_modo == 1:
            hora = self.tiempo_regresivo[0]["hora"]
            minuto = self.tiempo_regresivo[0]["minuto"]
            segundo = self.tiempo_regresivo[0]["segundo"]
            # poner valor de tiempo en pausa 1 = Regresivo
            if self.iniciar_modo[1] == "pause":
                self.salida_formateada[1] = self.tiempo_regresivo[0]["pause"]
                self.tiempo_en_pausa[1] = f"{hora:02d}:{minuto:02d}:{segundo:02d}"
                self.lineEdit_extra.setText(f"R {self.tiempo_en_pausa[1]}")  # info extra
            else:
                # almacena valor regresivo en pausa
                self.salida_formateada[1] = f"{hora:02d}:{minuto:02d}:{segundo:02d}"
                self.tiempo_regresivo[0]["pause"] = self.salida_formateada[1]

            self.lineEdit_hora.setText(str(self.salida_formateada[1]))# PONER tiempo REGRESIVO en display
        # -----------------------


        # MODO EVENTO valor 2  (calculo incremetar tiempo crono evento)
        if self.iniciar_modo[2] != "stop" and conteo == True:
            # calculo cronometro (MODO evento)
            self.tiempo_evento[0]["segundo"] += 1
            if self.tiempo_evento[0]["segundo"] == 60:
                self.tiempo_evento[0]["segundo"] = 0
                self.tiempo_evento[0]["minuto"] += 1
            if self.tiempo_evento[0]["minuto"] == 60:
                self.tiempo_evento[0]["minuto"] = 0
                self.tiempo_evento[0]["hora"] += 1
            if self.tiempo_evento[0]["hora"] == 99:
                self.tiempo_evento[0]["minuto"] = 0

        # MODO evento en pantalla el cronometro (evento) colocar avisos de eventos
        if self.ver_modo == 2:
            hora = self.tiempo_evento[0]["hora"]
            minuto = self.tiempo_evento[0]["minuto"]
            segundo = self.tiempo_evento[0]["segundo"]

            # comparar el display crono con los evento_actividad
            if len(self.tiempo_actividad) > 0 and self.iniciar_modo[2] == "start": # si hay actividades a leer en eventos
                if self.ventanas[8] is None:  # si le ventana no exite la abre
                    self.ventanas[8] = VerEvento_class()
                    self.ventanas[8].show()  # mostrar ventana seleccionada
                    self.ventanas[8].poner_color_fondo("#ffffff")  # poner color de fondo default
                    self.ventanas[8].move(self.pos_event[0], self.pos_event[1])
                    self.ventanas[8].resize(self.size_event[0], self.size_event[1])
                    self.ventanas[8].setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose) # Configurar para que se cierre cuando la ventana principal
                    self.ventanas[8].destroyed.connect(partial(self.limpiar_referencia, 8)) # Conectar señal de cierre para limpiar la referencia (SOLUCIÓN)
                    self.ventanas[8].poner_titulo_ventana(self.archivo_favorito)


                for indice, t_actividad in enumerate(self.tiempo_actividad) :
                    if t_actividad["actividad"] == f"{hora:02d}:{minuto:02d}:{segundo:02d}":
                        print(f"EVENTO ENCONTRADO: {t_actividad['tema']} ")
                        self.ventanas[8].poner_actividad(t_actividad["tema"]) # pone texto de actividad
                        self.ventanas[8].poner_color_fondo(t_actividad["bg"]) # poner color de fondo

                        #  mostrar actividad del evento
                        self.lineEdit_extra.setText(f"{indice +1}/{len(self.tiempo_actividad)}")  # actividad del  evento
                        self.ventanas[8].poner_titulo_ventana(f"{self.archivo_favorito} [{indice +1}/{len(self.tiempo_actividad)}]")


                        # Si ya existe la ventana restaurar tamaño
                        if self.ventanas[8].isMinimized(): # Si está minimizada, restaurarla
                            self.ventanas[8].showNormal()
                        elif not self.ventanas[8].isVisible(): # Si no está visible (pero no minimizada), mostrarla
                            self.ventanas[8].show()
                        # Si ya está visible, traerla al frente
                        self.ventanas[8].raise_()
                        self.ventanas[8].activateWindow()
                        break  # Rompe el ciclo

            # poner valor de tiempo en pausa 1 = Evento
            if self.iniciar_modo[2] == "pause":
                self.salida_formateada[2]  = self.tiempo_evento[0]["pause"]
                self.tiempo_en_pausa[2] = f"{hora:02d}:{minuto:02d}:{segundo:02d}"
                self.lineEdit_extra.setText(f"E {self.tiempo_en_pausa[2]}")  # info extra
            else:
                self.salida_formateada[2] = f"{hora:02d}:{minuto:02d}:{segundo:02d}"
                self.tiempo_evento[0]["pause"] = self.salida_formateada[2]

            self.lineEdit_hora.setText(str(self.salida_formateada[2])) # evento

        # -----------------------


        # ------------------------
        # MODO (hora) valor 3  mostrar salida cronometro
        self.formato_tiempo = "%I:%M:%S %p"  # formato de tiempo hora
        self.tiempo = self.now.strftime(self.formato_tiempo)
        if  self.ver_modo == 3:
           # poner valor de tiempo en pausa 3 = hora
            if self.iniciar_modo[3] == "pause":
                self.salida_formateada[3] = self.tiempo_hora[0]["pause"]
                self.tiempo_en_pausa[3] = f"{self.tiempo}"
                self.lineEdit_extra.setText(f"T {self.tiempo_en_pausa[3]}")  # info extra
            else:
                # almacena valor de hora en pausa display
                self.salida_formateada[3] = self.tiempo
                self.tiempo_hora[0]["pause"] = self.tiempo # ultima hora

            # poner hora en display
            self.lineEdit_hora.setText(str(self.salida_formateada[3])) # hora


        # -----------------------

        # ------------------------
        # EVALUAR alarma !!!!!!!!!
        if self.activar_alarma == "on":
            print("alarma activada")
            # cambiar color de fondo de la ventan alarma
            if self.ventanas[9] is not None:
                if self.intermitente_fondo_alarma == True:
                    self.ventanas[9].poner_color_fondo("#F3F944")  # poner color de fondo
                    self.intermitente_fondo_alarma = False
                else:
                    self.ventanas[9].poner_color_fondo("#FFFFFF")  # poner color de fondo
                    self.intermitente_fondo_alarma = True
            else:
                self.sound_effect.stop()  # para la alarma actual al cerrar
            # ---------------------
            # para evaluar alarma con el tiempo de cronometro
            time_str = self.lineEdit_hora.text()  # crono  mostrado actual
            if self.ver_modo == 3:
                # Reemplazamos tanto " AM" como " PM" por nada
                resultado = time_str.replace(" AM", "").replace(" PM", "")
                time_str = resultado.strip()

            maximo = len(self.tiempo_alarma) # maximo items alarmas
            for indice, alarma in enumerate(self.tiempo_alarma):
                # coincide el tiempo de alarma con cronometro progresivo
                if alarma["alarma"] == time_str:
                    print(f"Alarma N#{indice} {alarma['alarma']}")
                    # activar ventana VerAlarma y poner aviso
                    if self.ventanas[9] is None:
                        self.ventanas[9] = VerAlarma_class()
                        self.ventanas[9].show()
                    else:
                        self.ventanas[9].show()
                        # Si ya existe la ventana restaurar tamaño
                        if self.ventanas[9].isMinimized():
                            # Si está minimizada, restaurarla
                            self.ventanas[9].showNormal()
                        elif not self.ventanas[9].isVisible():
                            # Si no está visible (pero no minimizada), mostrarla
                            self.ventanas[9].show()
                        else:
                            # Si ya está visible, traerla al frente
                            self.ventanas[9].raise_()
                            self.ventanas[9].activateWindow()
                    # poner contenido a ventana alarma
                    print("* MOSTRAR [VerAlarma]")
                    self.ventanas[9].valor_alarma(self.tiempo_alarma[indice]["descripcion"])
                    self.ventanas[9].setWindowTitle(f"{indice + 1}/{maximo} Time: {time_str}")
                    # reproducir sonido de alarma
                    self.selected_file = self.tiempo_alarma[indice]["audio"]
                    self.play_sound()

                    self.ventanas[9].activateWindow()   # Asegura que la ventana tenga el foco
                    self.ventanas[9].raise_()           # Asegura que la ventana esté en primer plano
                    break  # rompe el ciclo de busqueda y comparacion de hora alarma (ya se encontro la alarma)


        # -----------------------

    # texto inicial del submenu MODO sin seleccionar items
    def texto_sin_seleccionar_menu_modo(self):
        self.actionCronometro_Progresivo.setChecked(False)
        self.actionCrono_Regresivo.setChecked(False)
        self.actionHora.setChecked(False)
        self.actionEvento.setChecked(False)

    # cambiar fondo para lineEdit_porte
    def fondo_lineEdit_porte(self, pos_color):
        palette = self.lineEdit_reporte.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(self.color_fondo_reporte[pos_color]))
        self.lineEdit_reporte.setPalette(palette)


    # actualizar display de cronometro
    def actualizar_display(self, indice):
        self.lineEdit_hora.setText(str(self.formateado[indice]))
        pass


    # ------------------------
    # METODOS PARA EVENTOS EN MENU MODO
    def progresiva(self):
        self.ver_modo = 0
        print(f"modo progresivo {self.ver_modo} {self.iniciar_modo}")
        self.lineEdit_hora.setText(str(self.salida_formateada[0]))
        self.lineEdit_reporte.setText(self.titulo_modo[0]) # progresivo
        self.lineEdit_extra.setText("")  # limpiar extra pasos
        self.fondo_lineEdit_porte(0) # cambiar color de lineEdit_reporte
        # ------
        self.texto_sin_seleccionar_menu_modo()
        self.actionCronometro_Progresivo.setChecked(True)
        self.cambiar_color_btn()  # cambiar btn al activarse

        # actualizar informacion en ventana editar crono (para modo progresivo
        if not (self.ventanas[1] is None):
            self.ventanas[1].comboBox_modo_crono.setCurrentIndex(0)
            self.ventanas[1].lineEdit_crono_edit.setText(self.salida_formateada[0])


    def regresiva(self):
        self.ver_modo = 1
        print(f"modo regresivo {self.ver_modo} {self.iniciar_modo}")
        self.lineEdit_hora.setText(str(self.salida_formateada[1]))
        self.lineEdit_reporte.setText(self.titulo_modo[1])  # progresivo
        self.fondo_lineEdit_porte(1)  # cambiar color de lineEdit_reporte
        self.lineEdit_extra.setText("")  # limpiar extra texto
        # ------
        self.texto_sin_seleccionar_menu_modo()
        self.actionCrono_Regresivo.setChecked(True)
        self.cambiar_color_btn()  # cambiar btn al activarse

        # actualizar informacion en ventana editar crono (para modo progresivo
        if not (self.ventanas[1] is None):
            self.ventanas[1].comboBox_modo_crono.setCurrentIndex(1)
            self.ventanas[1].lineEdit_crono_edit.setText(self.salida_formateada[1])


    def evento(self):
        self.ver_modo = 2  # pone modo evento
        print(f"modo evento {self.ver_modo} {self.iniciar_modo}")
        self.lineEdit_hora.setText(str(self.salida_formateada[2]))
        self.lineEdit_reporte.setText(self.titulo_modo[3])  # texto de reporte indica estado
        self.lineEdit_extra.setText("")  # limpiar extra texto
        self.fondo_lineEdit_porte(2)  # cambiar color de lineEdit_reporte
        # ------
        # estado del menu
        self.texto_sin_seleccionar_menu_modo()  # limpia seleccion en menu
        self.actionEvento.setChecked(True)
        self.cambiar_color_btn()  # indicar el estado btn para evento
        # ventana para mostrar texto de evento
        self.abrir_ventana(8)

        # actualizar informacion en ventana editar crono (para modo progresivo
        if not (self.ventanas[1] is None):
            self.ventanas[1].comboBox_modo_crono.setCurrentIndex(2)
            self.ventanas[1].lineEdit_crono_edit.setText(self.salida_formateada[2])


    def hora(self):
        self.ver_modo = 3 # pone modo hora
        print(f"modo hora {self.ver_modo}")
        self.lineEdit_hora.setText(str(self.salida_formateada[3]))
        self.lineEdit_reporte.setText(self.titulo_modo[2])  # Hora
        self.lineEdit_extra.setText("")  # limpiar pasos en evento
        self.fondo_lineEdit_porte(3)  # cambiar color de lineEdit_reporte
        # ------
        self.texto_sin_seleccionar_menu_modo()
        self.actionHora.setChecked(True)
        self.cambiar_color_btn()  # indicar el estado btn para hora



    def alarma(self):
        print("poner alarma")

    def editar_evento(self):
        print("poner editar evento")

    def configuracion(self):
        print("configuracion evento")

    def reg_pausas(self):
        print("registro de pausas")

    def salida(self):
        print("salida")
        exit()

    # ---------------------------
    # METODOS PARA EVENTOS EN MENU ACCION
    def borrar(self):
        print("borrar pantalla")

    def editar(self):
        print("editar pantalla de cronometro")

    # -------------------------------------
    # METODOS PARA Abrir nuevas ventanas
    def abrir_ventana(self, index):
        """
                listado de ventanas auxiliares
                parametro usado en metodo self.abrir_ventana(n)
                0 = (SIN USO)
                1 = editar chronometro
                2 = acerca
                3 = ayuda
                4 = editar evento
                5 = (SIN USO)
                6 = registro de pausas
                7 = alarma
                8 = event0
                10 = lincecia
        """
        # CREAR VENTANAS verifica que la lista este en None para crear la ventana
        if self.ventanas[index] is None:

            # VENTANA Borrar CHRONOMETRO (disable)
            if index == 0:
                pass

            # VENTANA EDITAR CHRONOMETRO
            if index == 1:
                self.ventanas[index] = EditarCrono_class(self, self.lang) # con self pasa la clase main
                print("ventana editar valores crono")

            # VENTANA ACERCA
            if index == 2:
                self.ventanas[index] = Acerca_class(self.lang) # ventana de acerca con diferente idiomas
                print(f"ventana acerca {self.lang}")

            # VENTANA AYUDA
            if index == 3:
                self.ventanas[index] = Ayuda_class(self.lang) # se pasa lang
                print("ventana Ayuda")

            # VENTANA EDITAR EVENTO
            if index == 4:
                self.ventanas[index] = EditarEvento_class(self, self.lang)  # se pasan self y lang
                print("ventana Editar Evento")

            # VENTANA Configuracion
            if index == 5:
                self.ventanas[index] = EditConfig_class(self, self.lang) # pasa self
                print("ventana configuracion")

            # VENTANA Historico de Pausa
            if index == 6:
                self.ventanas[index] = HistoricoPausa_class(self, self.lang) # se pasan self y lang
                print("ventana Historico Pausa")

            # VENTANA Alarma
            if index == 7:
                self.ventanas[index] = EditarAlarma_class(self, self.lang) # se pasa self y lang
                if self.activar_alarma == "on":
                    self.ventanas[index].checkBox_activar.setChecked(True) # poner activo el checkbox
                print("ventana editar Alarma")

            # VENTANA Evento (ver)
            if index == 8:
                print("ventana Evento")
                self.ventanas[index] = VerEvento_class()
                self.ventanas[index].poner_titulo_ventana(self.archivo_favorito)
                self.ventanas[8].poner_color_fondo("#ffffff")  # poner color de fondo default
                self.ventanas[8].move(self.pos_event[0], self.pos_event[1])
                self.ventanas[8].resize(self.size_event[0], self.size_event[1])

            # VENTANA Licencia
            if index == 10:
                self.ventanas[index] = Licencia_class()  # ver licencia
                print("ventana Licencia")

            self.ventanas[index].show() # mostrar ventana seleccionada
            # Configurar para que se cierre cuando la ventana principal se cierre
            self.ventanas[index].setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            # Conectar señal de cierre para limpiar la referencia (SOLUCIÓN)
            self.ventanas[index].destroyed.connect(partial(self.limpiar_referencia, index))

        else:
            # si ventana ver_evento existe
            if index == 8:
                self.ver_modo = 2  # pone modo evento
                print(f"modo evento {self.ver_modo} {self.iniciar_modo}")
                self.lineEdit_reporte.setText("Evento")  # texto de reporte indica estado
                self.texto_sin_seleccionar_menu_modo()  # limpia seleccion en menu
                self.actionEvento.setChecked(True)
                self.cambiar_color_btn()  # indicar el estado btn para evento
                print("ventana Evento")

            # para todas las subventanas
            # Si ya existe la ventana restaurar tamaño
            if self.ventanas[index].isMinimized():
                # Si está minimizada, restaurarla
                self.ventanas[index].showNormal()
            elif not self.ventanas[index].isVisible():
                # Si no está visible (pero no minimizada), mostrarla
                self.ventanas[index].show()
            else:
                # Si ya está visible, traerla al frente
                self.ventanas[index].raise_()
                self.ventanas[index].activateWindow()

    # metodo para limpiar instancia de ventanas creadas
    def limpiar_referencia(self, index):
        """Método para limpiar la referencia de la ventana cerrada"""
        self.ventanas[index] = None
        print(f"Ventana {index} cerrada, referencia limpiada")


    # -------------------------
    # METODOS PARA EVENTO EN BOTONES
    def pausa(self):
        if  self.iniciar_modo[self.ver_modo] != "pause":
            print(f"poner pausa modo {self.ver_modo}")
            self.iniciar_modo[self.ver_modo] = "pause"
            self.update(False)
            # poner prefijos para los modos de pausa
            prefijos =["P","R","E","T"] # P= progresivo, R= regresivo, E= evento, T = tiempo
            self.memoria_pausa.append(f"{prefijos[self.ver_modo]} {self.lineEdit_hora.text()}") # agrega el tiempo para el historico de pausa
            self.memoria_pausa_info.append("") # agrega info vacio de pausa
            # actualiza automaticamente la Qtablawidget si la ventana historico existe
            if not (self.ventanas[6] is None):
                self.ventanas[6].refrescar_tabla()  # refrescar tabla para carcar

            print(self.memoria_pausa)
        else:
            print(f"quitar pausa modo {self.ver_modo}")
            self.lineEdit_hora.setText(f"{self.tiempo_en_pausa[self.ver_modo]}")  # poner ultimo tiempo antes de conteo en display
            self.iniciar_modo[self.ver_modo] = "start"

        print(f"PAUSA: {self.ver_modo} {self.iniciar_modo}")
        self.cambiar_color_btn()  # cambiar color btn al activarse

    # iniciar cronometro
    def iniciar(self):
        self.iniciar_modo[self.ver_modo] = "start"
        self.cambiar_color_btn()  # cambiar color btn al activarse
        print("iniciar cronometro")
        print(self.iniciar_modo)

    # parar cronometro
    def parar(self):
        self.sound_effect.stop()  # para sonido de la alarma actual
        self.iniciar_modo[self.ver_modo] = "stop"
        self.cambiar_color_btn()  # cambiar color btn al activarse
        print(self.iniciar_modo)
        print("parar cronometro")

    # ocultar o mostrar barra de menu
    def ocultar_barra_menu(self, state):
        if state == Qt.CheckState.Checked.value:
            print("El QCheckBox está marcado.")
            self.menubar.setVisible(True) # muesta menubar

        else:
            print("El QCheckBox no está marcado.")
            self.menubar.setVisible(False) # oculta menubar


    # boton para borrar un modo seleccionado
    def btn_borrar(self):
        if self.ver_modo == 0:
            print("borrando progresivo")
            self.menu_borrar_solo_progresivo()
        if self.ver_modo == 1:
            print("borrando regresivo")
            self.menu_borrar_solo_regresivo()
        if self.ver_modo == 2:
            print("borrando evento")
            self.menu_borrar_solo_evento()


    # ------------------------------
    # eventos de submenu borrar
    # ------------------------------

    # menu borrar todod
    def menu_borrar_todo(self):
        print("Borrar todo y Parar")
        self.menu_parar_todo() # metodo para poner todo los contadores en estado incial
        self.menu_borrar_solo_progresivo()
        self.menu_borrar_solo_regresivo()
        self.menu_borrar_solo_evento()

    # menu borrar solo progresivo
    def menu_borrar_solo_progresivo(self):
        print("borrar crono progresivo")
        self.tiempo_progresivo[0]["hora"] = 0
        self.tiempo_progresivo[0]["minuto"] = 0
        self.tiempo_progresivo[0]["segundo"] = 0
        self.lineEdit_extra.setText("") # texto extra

    # menu borrar solo regresivo
    def menu_borrar_solo_regresivo(self):
        print("borrar crono regresivo")
        self.tiempo_regresivo[0]["hora"] = 0
        self.tiempo_regresivo[0]["minuto"] = 0
        self.tiempo_regresivo[0]["segundo"] = 0
        self.lineEdit_extra.setText("")  # texto extra

    # menu borrar solo evento
    def menu_borrar_solo_evento(self):
        print("borrar solo evento")
        self.tiempo_evento[0]["hora"] = 0
        self.tiempo_evento[0]["minuto"] = 0
        self.tiempo_evento[0]["segundo"] = 0
        self.lineEdit_extra.setText("")  # texto extra

    # menu parar todos
    def menu_parar_todo(self):
        print("parar todos los cronometros")
        self.iniciar_modo[0] = "stop"  # progresivo
        self.iniciar_modo[1] = "stop"  # regresivo
        self.iniciar_modo[2] = "stop"  # evento
        self.iniciar_modo[3] = "start"  # hora
        self.cambiar_color_btn()  # cambiar color btn al activarse
    # --------------------------------


# funcion para poner colores claros en tema fusion
def set_fusion_light_palette(app):
    """Establecer paleta clara de Fusion (por defecto)"""
    palette = QPalette()

    # Colores para tema claro Fusion
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

    app.setPalette(palette)


# ===============================================
# Solo ejecuta si es el archivo principal
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_Cronometro()
    # Solo informar, no forzar
    current_style = app.style().name()
    print(f"Ejecutando con estilo: {current_style}")
    # Forzar paleta de colores (elige una)
    set_fusion_light_palette(app)  # Para tema claro

    app.exec()
# ===============================================