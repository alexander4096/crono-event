# esta clase se comunica con la clase main_window para actualizar
#  el submenu de evento al modificar el listado

import os # uso de rutas y sistema de archivo
import sys

from PyQt6 import QtWidgets
from PyQt6 import uic
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QCloseEvent, QAction
from PyQt6.QtWidgets import QMessageBox, QMenu, QApplication, QHeaderView
from translations import translation_manager # manejador de idiomas
from PyQt6.QtWidgets import QTableWidget
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox

# ------------------------------
# clase ventana Historico de Pausa (6)
# ------------------------------
class HistoricoPausa_class(QtWidgets.QDialog):
    def __init__(self,  main_window, idioma):
        super().__init__()
        self.main_window = main_window  # Guarda la referencia a la instancia de A

        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint) # poner al frente

        # cargar GUI
        # 1. Obtiene la ruta absoluta de la carpeta donde está este archivo (src/)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # 2. Construye la ruta subiendo un nivel y entrando a /gui
        # '..' significa "subir una carpeta"
        path_ui = os.path.join(BASE_DIR, "gui", "histo_pausa.ui")

        # 3. Carga la interfaz
        if os.path.exists(path_ui):
            uic.loadUi(path_ui, self)
        else:
            print(f"Error: No se encontró el archivo UI en: {path_ui}")

        # inicializar variables
        self.datos_guardados = {}


        # configuracion de tabla
        self.tableWidget.setRowCount(0)  # filas iniciales
        self.tableWidget.setColumnCount(2)
        # formato de las columnas
        header = self.tableWidget.horizontalHeader()
        # Primera columna tamaño fijo
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # ancho fijo
        header.resizeSection(0, 90)  # 90 píxeles
        # Segunda columna se expande
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # ancho dinamico

        # Configurar tabla para menú contextual
        self.tableWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.showContextMenu)

        # CARGAR el idioma de la ventana
        self.cargar_idioma(idioma)

        # Establece el título de la ventana
        self.limpiar_tabla()      # Limpiar lista en QListWidget
        self.cargar_tabla("all")  # cargar lista en QListWidget

        # eventos botones
        self.pushButton_limpiar.clicked.connect(self.borrar_historico_tabla)    # btn limpiar
        # Conectar señal para detectar cambios
        self.tableWidget.cellChanged.connect(self.on_cell_changed)


    # Menu contextual para copiar al porta papel
    def showContextMenu(self, pos: QPoint):
        # Crear menú contextual
        context_menu = QMenu(self)

        # Acción para copiar fila seleccionada
        copy_row_action = QAction(translation_manager.get_ui_text("qmenu_linea_1"), self)
        copy_row_action.triggered.connect(self.copySelectedRow)
        context_menu.addAction(copy_row_action)

        # Acción para copiar toda la tabla
        copy_all_action = QAction(translation_manager.get_ui_text("qmenu_linea_2"), self)
        copy_all_action.triggered.connect(self.copyAllTable)
        context_menu.addAction(copy_all_action)

        # Mostrar menú en la posición del clic
        context_menu.exec(self.tableWidget.viewport().mapToGlobal(pos))

    def copySelectedRow(self):
        # Obtener filas seleccionadas
        selected_rows = self.tableWidget.selectionModel().selectedRows()

        if not selected_rows:
            title = translation_manager.get_message("titulo 3")
            content = translation_manager.get_message("contenido 3")
            QMessageBox.information(self, title,
                                        content)
            return

        # Construir texto para el portapapeles
        clipboard_text = ""

        for row_index in sorted([row.row() for row in selected_rows]):
            row_data = []
            for col in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row_index, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")

            clipboard_text += "\t".join(row_data) + "\n"

        # Copiar al portapapeles
        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_text.strip())
        # esto es para indicar resultado de la copia por seleccion
        title = translation_manager.get_message("titulo 4")
        content = translation_manager.get_message("contenido 4")
        QMessageBox.information(self, title,
                                f'{len(selected_rows)} {content}')

    def copyAllTable(self):
        # Construir texto para el portapapeles con toda la tabla
        clipboard_text = ""

        # Encabezados
        headers = []
        for col in range(self.tableWidget.columnCount()):
            headers.append(self.tableWidget.horizontalHeaderItem(col).text())
        clipboard_text += "\t".join(headers) + "\n"

        # Filas de datos
        for row in range(self.tableWidget.rowCount()):
            row_data = []
            for col in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")

            clipboard_text += "\t".join(row_data) + "\n"

        # Copiar al portapapeles
        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_text.strip())
        # aviso de copia toda la tabla
        title = translation_manager.get_message("titulo 5")
        content = translation_manager.get_message("contenido 5")
        QMessageBox.information(self, title,
                                content)

    # -------------------------------------------
    # captura el evento cuando modifica las celdas por el usuario en TableView
    def on_cell_changed(self, row, column):
        columna2_completa = []

        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, 1)  # Columna 1 (segunda)
            if item and item.text():
                columna2_completa.append(item.text())
            else:
                columna2_completa.append("")  # Valor vacío para celdas sin datos

        self.main_window.memoria_pausa_info = columna2_completa
        print(f"modificada columna: {columna2_completa}")



    # CARGAR el idioma de la ventana
    def cargar_idioma(self, idioma):
        self.current_language = idioma  # idioma por defecto
        self.ui = "ui_historico_pausa"  # nombre del JSON UI para la ventana edit_event
        self.message = "messages_historico_pausa"  # nombre del JSON mensaje para la ventna edit_event
        translation_manager.set_language(self.current_language)  # actualizar idioma seleccionado
        translation_manager.set_name_ui(self.ui, self.message)
        self.update_texts()  # actualiza el texto del idioma seleccionado


    # idioma de la ventana actualiza
    def update_texts(self):
        self.setWindowTitle(translation_manager.get_ui_text("window_title"))
        self.label_1.setText(translation_manager.get_ui_text("label_1"))
        self.pushButton_limpiar.setText(translation_manager.get_ui_text("pushButton_limpiar"))

        col1 = translation_manager.get_ui_text("titulo_tabla")[0]
        col2 = translation_manager.get_ui_text("titulo_tabla")[1]
        self.tableWidget.setHorizontalHeaderLabels([col1, col2])  # nombre los titulos table


    def closeEvent(self, event: QCloseEvent):
        """Maneja el evento de cierre de la ventana"""
        print("⚠️  ventana Historico de Pausa cerrando...")
        event.accept()

    # cargar historico de pausa
    def cargar_tabla(self, modo):
        # si esta ventan existe
        # print(f" lista: === {len(self.main_window.memoria_pausa)}")

        # cargar solo un item con la ventana abierta
        if modo =="one":
            if not self.main_window is None:  # si existe clase main_window ejecuta el metodo
                # cargar nuevamente la tabla
                row = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row)
                self.tableWidget.setItem(row, 0, QTableWidgetItem(str(self.main_window.memoria_pausa[row])))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(""))  # info para el usuario
            else:
                title = translation_manager.get_message("Error 1")
                content = translation_manager.get_message("contenido 1")
                QMessageBox.information(
                    self,
                    title,
                    content
                )

        # cargar toda la tabla cuando se cierra la ventana
        if modo =="all":
            if not self.main_window is None:  # si existe clase main_window ejecuta el metodo
                for indice, i in enumerate(self.main_window.memoria_pausa):
                    row = self.tableWidget.rowCount()
                    self.tableWidget.insertRow(row)
                    self.tableWidget.setItem(row, 0, QTableWidgetItem(str(i)))
                    self.tableWidget.setItem(row, 1, QTableWidgetItem(str(self.main_window.memoria_pausa_info[indice])))  # info para el usuario


    # limpiar historico de pausa
    def limpiar_tabla(self):
        print("limpiar QtableView historico pausa")
        # self.tableWidget.clear()
        self.tableWidget.clearContents()  # Limpia el contenido
        self.tableWidget.setRowCount(0)  # Elimina todas las filas


    # BTN borrar historico de tabla
    def borrar_historico_tabla(self):
        if not self.main_window is None:  # si existe clase main_window ejecuta el metodo
            # configrmacion para borrar
            respuesta = QMessageBox.question(
                self,  # Ventana padre
                "Confirmar borrado",  # Título
                "¿Desea borrar la tabla?",  # Mensaje
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  # Botones
                QMessageBox.StandardButton.No  # Botón por defecto
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                print("Usuario dijo SÍ")
                self.main_window.memoria_pausa.clear()  # limpia memoria de tiempo pausa
                self.main_window.memoria_pausa_info.clear()  # limpiar descripcion de tiempo pausa
                self.limpiar_tabla()
            else:
                print("Usuario dijo NO")
            # ----------------------------
        else:
            title = translation_manager.get_message("Error 2")
            content = translation_manager.get_message("contenido 2")
            QMessageBox.information(
                self,
                title,
                content
            )

    # btn refrescar tabla (metodo que llama main para cargar nuevos datos
    def refrescar_tabla(self):

        self.cargar_tabla("one")



# ---------------------------------------------
# Solo ejecuta si es el archivo principal
if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = HistoricoPausa_class(None, "english")
    window.show()
    app.exec()
