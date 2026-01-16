# funciona !! 23/10/2024
import sys
import os # uso de rutas y sistema de archivo
import json
from PyQt6 import QtWidgets
from PyQt6 import uic
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QCloseEvent, QAction
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtWidgets import QMessageBox, QListWidget, QMenu, QApplication




# librerias personales
from translations import translation_manager # manejador de idiomas
import ruta_archivo_linux as datafile               # ruta de archivos para guardar datos de usuario en linux

# ------------------------------
# clase ventana EditarAlarma (7)
# ------------------------------
class EditarAlarma_class(QtWidgets.QDialog):
    def __init__(self,  main_window, idioma):
        super().__init__()
        self.main_window = main_window  # Guarda la referencia a la instancia de A

        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint) # poner al frente

        # cargar GUI
        # 1. Obtiene la ruta absoluta de la carpeta donde está este archivo (src/)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # 2. Construye la ruta subiendo un nivel y entrando a /gui
        # '..' significa "subir una carpeta"
        path_ui = os.path.join(BASE_DIR, "gui",  "edit_alarma.ui")

        # 3. Carga la interfaz
        if os.path.exists(path_ui):
            uic.loadUi(path_ui, self)
        else:
            print(f"Error: No se encontró el archivo UI en: {path_ui}")


        self.sound_effect = QSoundEffect()  # cargar reproducto de audio
        # CARGAR el idioma de la ventana
        self.cargar_idioma(idioma)

        self.lineEdit_horaAlarma.setInputMask("00:00:00; ") # mascara numerica

        # valores iniciales
        self.selected_file = ""
        self.hh_int = 0
        self.mm_int = 0
        self.ss_int = 0
        self.activar_alarma = "off"  # estado de la alarma
        self.lineEdit_horaAlarma.setText("00:00:00")
        self.tiempo_alarma = []  # Lista con descripcion de alarmas activas
        self.actualizar_listado()  # actualiza el listado y ordena
        self.wav_dir = "wav"  # Subdirectorio donde están los archivos .wav
        self.volume = 0.4     # valor del volumen 0.0 a 1.0
        self.estado_sonido = "PLAY" # estado del sonido


        # Configurar menú contextual
        self.setup_context_menu()
        self.cargar_combobox_loadWavFiles() # cargar combobox con archivos wav

        # cargar alarmas grabadas
        self.leer_archivo_alarma()

        # EVENTOS botones
        self.pushButton_agregar.clicked.connect(self.agregar)  # iniciar
        self.pushButton_quitar.clicked.connect(self.quitar)  # pausa
        self.checkBox_activar.stateChanged.connect(self.check_alarma)        # QCheckBox estado activar / desactivar alarma
        self.pushButton_borrar.clicked.connect(self.limpiar_campos)          # limpiar campos
        self.pushButton_salvar.clicked.connect(self.grabar_archivo_alarma)   # boton de salvar
        # seleccionar una alarma de la lista
        self.listWidget_listado_alarma.itemSelectionChanged.connect(self.mostrar_elemento_seleccionado)
        self.comboBox_audio.currentIndexChanged.connect(self.seleccionar_sonido)
        self.pushButton_play.clicked.connect(self.play_sound) # tocar o parar sonido
        # evento de sonido
        self.sound_effect.playingChanged.connect(self.on_playing_changed)

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
        time_str = self.lineEdit_horaAlarma.text()
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
        self.lineEdit_horaAlarma.setText(f"{self.hh_int:02d}:{self.mm_int:02d}:{self.ss_int:02d}")





    # ----------------------------------------
    # BLOQUE de MENU CONTEXTUAL para copiar contenido de QlistWidget a la papelera
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


    def play_sound(self):
        # Crear el reproductor de sonido
        """Alterna entre reproducir y pausar"""
        if self.sound_effect.isPlaying():
            self.sound_effect.stop()
        else:
            self.play_audio()

    def play_audio(self):
        """Reproduce el archivo WAV seleccionado"""
        try:
            # Configurar QSoundEffect
            self.current_file = os.path.join(self.wav_dir, self.selected_file)
            print(f" sonar = {self.current_file} {self.selected_file}")
            self.sound_effect.setSource(QUrl.fromLocalFile(self.current_file))
            self.sound_effect.setVolume(self.volume)
            self.sound_effect.play()  # Reproduci

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo reproducir el archivo:\n{str(e)}")

    # se ejecuta cuando termina la reproduccion del wav
    def on_playing_changed(self):
        self.pushButton_play.setText(str("■")) # parar
        self.estado_sonido = "STOP"
        # Se ejecuta cuando el estado de reproducción cambia"""
        if not self.sound_effect.isPlaying():
            self.pushButton_play.setText(str("▶"))  # play
            self.estado_sonido = "PLAY"
            print("Reproducción completada")

    # Seleccionar sonido en combobox
    def seleccionar_sonido(self):
        self.selected_file = self.comboBox_audio.currentText()
        print(f"sonido seleccionado : {self.selected_file}")
        self.pushButton_play.setText(str("▶")) #  play sign



        # cargar QCombobox Widget
    def cargar_combobox_loadWavFiles(self):
        """Carga los archivos .wav desde el subdirectorio"""
        try:
            # Limpiar el ComboBox actual
            self.comboBox_audio.clear()

            # Verificar si el directorio existe
            if not os.path.exists(self.wav_dir):
                print(f"Error: Directorio '{self.wav_dir}' no existe")
                return

            # Obtener lista de archivos .wav
            wav_files = []
            for file in os.listdir(self.wav_dir):
                if file.lower().endswith('.wav'):
                    wav_files.append(file)

            wav_files.sort()
            # Agregar al ComboBox
            self.comboBox_audio.addItems(wav_files)

            # Seleccionar el primer elemento si existe
            self.comboBox_audio.setCurrentIndex(2) # 2
            self.selected_file = self.comboBox_audio.currentText() # archivo de audio previo seleccionado

        except Exception as e:
            print(f"Error: {str(e)}")


    # CARGAR el idioma de la ventana
    def cargar_idioma(self, idioma):
        self.current_language = idioma  # idioma por defecto
        self.ui = "ui_edit_alarm"  # nombre del JSON UI para la ventana edit_event
        self.message = "messages_edit_alarm"  # nombre del JSON mensaje para la ventna edit_event
        translation_manager.set_language(self.current_language)  # actualizar idioma seleccionado
        translation_manager.set_name_ui(self.ui, self.message)
        self.update_texts()  # actualiza el texto del idioma seleccionado
        # menuContextual traduccion a idioma seleccionado
        self.qmenu_linea_1 = translation_manager.get_ui_text("qmenu_linea_1")
        self.qmenu_linea_2 = translation_manager.get_ui_text("qmenu_linea_2")

    # idioma de la ventana actualiza
    def update_texts(self):
        self.setWindowTitle(translation_manager.get_ui_text("window_title"))
        self.label_1.setText(translation_manager.get_ui_text("label_1"))
        self.label_2.setText(translation_manager.get_ui_text("label_2"))
        self.label_3.setText(translation_manager.get_ui_text("label_3"))
        self.label_4.setText(translation_manager.get_ui_text("label_4"))
        self.pushButton_borrar.setText(translation_manager.get_ui_text("pushButton_borrar"))
        self.pushButton_salvar.setText(translation_manager.get_ui_text("pushButton_salvar"))
        self.checkBox_activar.setText(translation_manager.get_ui_text("checkBox_activar"))


    def closeEvent(self, event: QCloseEvent):
            """Maneja el evento de cierre de la ventana"""
            print("⚠️  ventana Alarma cerrando...")
            self.sound_effect.stop()  # parar audio
            event.accept()

    # revisar estado de checkbox widget y mandar valor a clase principal crono
    def check_alarma(self, state):
        if not self.main_window is None:  # si existe clase main_window ejecuta el metodo
            # Verificar el estado del QCheckBox
            if state == Qt.CheckState.Checked.value:
                print("El QCheckBox está marcado.")
                self.activar_alarma = "on"
                self.main_window.tiempo_alarma = self.tiempo_alarma   # se pasa listado de alarma a ventana ppal para evaluar
                self.main_window.activar_alarma = self.activar_alarma # se pasa la activacion de alarma
                self.main_window.marcar_alarma_activa("on")
            else:
                print("El QCheckBox no está marcado.")
                self.activar_alarma = "off"
                self.main_window.tiempo_alarma.clear() # limpia listado
                self.main_window.activar_alarma = self.activar_alarma  # se pasa la activacion de alarma
                self.main_window.marcar_alarma_activa("off")
        else:
            title = translation_manager.get_message("Error 1")
            content = translation_manager.get_message("contenido 1")
            QMessageBox.information(
                self,
                 title,
                 content
            )

    # truncar texto de tema si pasa mas de 55 chars
    def truncar_texto(self, texto, max_caracteres):
        if len(texto) > max_caracteres:
            return texto[:max_caracteres - 3] + "..."
        return texto

    # actualizar listado de alarma en memoria
    def actualizar_listado(self):
        # Ordenar la lista usando la clave convertida
        self.tiempo_alarma.sort(key=lambda x: self.tiempo_a_segundos(x["alarma"]))
        # Agrega cada valor de "alarma" al QListWidget
        self.listWidget_listado_alarma.clear() # limpia previamente
        for alarma in self.tiempo_alarma:
            descrip = self.truncar_texto(alarma['descripcion'], 40)  # Truncar a 45 chars
            salida = f"{alarma["alarma"]} | {descrip}"
            self.listWidget_listado_alarma.addItem(salida)


    # agregar hora de alarma
    def agregar(self):
        if self.validacion() == "ok":
            print("agregar alarma")

            # Si encontro alarma modificar descripcion
            alarma_nueva = True # confirmar si es nuevo el item de alarma
            for index, alarma in enumerate(self.tiempo_alarma):
                if alarma["alarma"] == f"{self.hh_int:02d}:{self.mm_int:02d}:{self.ss_int:02d}":
                    alarma_nueva = False
                    self.tiempo_alarma[index]["descripcion"] =  self.lineEdit_descripcion.text()
                    self.selected_file = self.comboBox_audio.currentText()
                    self.tiempo_alarma[index]["audio"] = self.selected_file

            # no se encontro alarma es nueva
            if alarma_nueva:
                # almacer una nueva alarma en listado
                hora_formateada = f"{self.hh_int:02d}:{self.mm_int:02d}:{self.ss_int:02d}"
                descripcion = self.lineEdit_descripcion.text()
                self.tiempo_alarma.append({"alarma": hora_formateada,
                                           "descripcion": descripcion,
                                           "audio":self.selected_file})
                print(f"agregar item: {self.tiempo_alarma}")  # Salida: alarma, descripcion, audio 00:01:01

        # limpiar campos y actualizar
        self.listWidget_listado_alarma.clear() # limpiar listWidget
        print("limpiar despues de agregar")
        self.limpiar_campos()  # limpiar campos
        self.actualizar_listado() # actualiza el listado y ordena

    # metodo para validacion de entrada de campo tiempo alarma
    def validacion(self):
        print("validar alarma")
        salida = "ok"
        # Obtener el texto del QLineEdit
        time_str = self.lineEdit_horaAlarma.text()
        # Separar hh, mm, ss
        hh, mm, ss = time_str.split(":")

        # Validar los valores
        self.hh_int = int(hh) if hh else 0
        self.mm_int = int(mm) if mm else 0
        self.ss_int = int(ss) if ss else 0

        # validacion cuando la hora es 00:00:00 no se ha fijado un tiempo
        if self.hh_int == 0 and self.mm_int == 0 and self.ss_int == 0:
            title = translation_manager.get_message("Error 2")
            content = translation_manager.get_message("contenido 2")
            QMessageBox.warning(
                self,
                title,
                content
            )
            salida = "fail"



        return salida

    # limpiar campos
    def limpiar_campos(self):
        self.lineEdit_horaAlarma.setText("00:00:00")
        self.lineEdit_descripcion.setText("")

    # quitar hora de alarma
    def quitar(self):
        print("quitar alarma")
        row = self.listWidget_listado_alarma.currentRow()
        if row >= 0:
            # Buscar el diccionario que contiene la hora específica
            hora_a_eliminar = self.lineEdit_horaAlarma.text()

            for index, alarma in enumerate(self.tiempo_alarma):
                print(f"{hora_a_eliminar} == {alarma}")
                if alarma["alarma"] == hora_a_eliminar:
                    del self.tiempo_alarma[index] # lista con diccionario
                    break  # Rompe el ciclo una vez eliminado

            self.actualizar_listado()  # actualiza el listado y ordena
            self.limpiar_campos() # limpiar campos

        else:
            title = translation_manager.get_message("Error 4")
            content = translation_manager.get_message("contenido 4")
            QMessageBox.warning(
                self,
                title,
                content
            )


    # Función para convertir "hh:mm:ss" a segundos
    def tiempo_a_segundos(self, tiempo_str):
        h, m, s = map(int, tiempo_str.split(':'))
        return h * 3600 + m * 60 + s

    def mostrar_elemento_seleccionado(self):
        try:
            index = self.listWidget_listado_alarma.currentRow()  # fila seleccionada
            print(f"seleccionar item = {index} / {len(self.tiempo_alarma)}")
            if len(self.tiempo_alarma) > 0:
                self.lineEdit_horaAlarma.setText(self.tiempo_alarma[index]["alarma"])
                self.lineEdit_descripcion.setText(self.tiempo_alarma[index]["descripcion"])
                # Encontrar el índice basado en el texto
                indice = self.comboBox_audio.findText(self.tiempo_alarma[index]["audio"])
                self.comboBox_audio.setCurrentIndex(indice) # audio seleccionado
            else:
                # no se muestra nada se limpia
                self.limpiar_campos()  # limpiar campos
        except IndexError as e:
            pass
            # desmarcar si se borra el final

    # -------------------------------------------
    # cargar y grabar configuracion de alarma en archivo json

    # graba alarma en disco
    def grabar_archivo_alarma(self):
        try:
            archivo_json = os.path.join(datafile.app_config_dir, "alarmas.json")
            # Guardar en archivo JSON
            with open(archivo_json, 'w', encoding='utf-8') as f:
                json.dump(self.tiempo_alarma, f, indent=4, ensure_ascii=False)
            print(f"✓ Datos guardados exitosamente en: {archivo_json}")
            title = translation_manager.get_message("titulo 5")
            content = translation_manager.get_message("contenido 5")
            QMessageBox.information(
                self,
                title,
                content
            )

        except PermissionError:
            print(f"✗ Error: No tienes permisos para escribir en {archivo_json}")
        except IOError as e:
            print(f"✗ Error de E/S al guardar: {e}")
        except Exception as e:
            print(f"✗ Error inesperado al guardar: {e}")

    # lee alarma en disco
    def leer_archivo_alarma(self):
        # Definir rutas
        archivo_json = os.path.join(datafile.app_config_dir, "alarmas.json")

        # Leer desde archivo JSON
        try:
            with open(archivo_json, 'r', encoding='utf-8') as f:
                self.tiempo_alarma = json.load(f)
            print(f"Datos cargados desde: {archivo_json}")
            print(f"Contenido: {self.tiempo_alarma}")
            # limpiar campos
            self.limpiar_campos()  # limpiar campos
            # actualizar lisbox
            self.actualizar_listado()  # actualiza el listado y ordena
        except FileNotFoundError:
            print(f"El archivo {archivo_json} no existe")
            self.tiempo_alarma = []  # Inicializar vacío si no existe
        except json.JSONDecodeError:
            print(f"Error al leer el archivo JSON: {archivo_json}")
            self.tiempo_alarma = []



# ---------------------------------------------
# Solo ejecuta si es el archivo principal
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = EditarAlarma_class(None, "english")
    window.show()

    app.exec()
