import json
import os
import sys
from datetime import datetime

from PyQt5.QtCore import QEvent, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QDoubleValidator, QFont, QKeySequence, QPalette
from PyQt5.QtWidgets import (
    QAction,
    QActionGroup,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro6_datos.json")

TITULO = "SISTEMA DE REGISTRO"

CARRERAS = [
    "Ingeniería en Sistemas",
    "Ingeniería Electrónica",
    "Ingeniería Civil",
    "Contaduría",
    "Administración",
    "Psicología",
    "Derecho",
    "Medicina",
    "Arquitectura",
]

ACENTOS = ["#00f0ff", "#ff2bd6", "#39ff14", "#ff9f1c", "#7b5cff"]

TEMA = """
QWidget {{
    background-color: #05060f;
    color: {acento};
    font-family: 'Consolas', 'Courier New', monospace;
}}
QMenuBar {{ background-color: #0b0f1e; border-bottom: 1px solid {acento}; }}
QMenuBar::item {{ padding: 6px 12px; background: transparent; }}
QMenuBar::item:selected {{ background-color: {acento}; color: #05060f; }}
QMenu {{ background-color: #0b0f1e; border: 1px solid {acento}; }}
QMenu::item {{ padding: 6px 24px 6px 20px; }}
QMenu::item:selected {{ background-color: {acento}; color: #05060f; }}
QMenu::separator {{ height: 1px; background: {acento}; margin: 4px 8px; }}
QLineEdit, QTextEdit, QComboBox {{
    background-color: #0b0f1e;
    border: 1px solid {acento};
    border-radius: 4px;
    padding: 5px;
    selection-background-color: {acento};
    selection-color: #05060f;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{ border: 2px solid {acento}; }}
QPushButton {{
    background-color: #0b0f1e;
    border: 1px solid {acento};
    border-radius: 4px;
    padding: 7px 12px;
    color: {acento};
    font-weight: bold;
}}
QPushButton:hover {{ background-color: {acento}; color: #05060f; }}
QPushButton:pressed {{ background-color: #ffffff; color: {acento}; }}
QGroupBox {{
    border: 1px solid {acento};
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 10px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {acento};
    font-weight: bold;
}}
QCheckBox, QRadioButton {{ spacing: 8px; color: {acento}; }}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 15px;
    height: 15px;
    border: 1px solid {acento};
    background-color: #0b0f1e;
}}
QRadioButton::indicator {{ border-radius: 8px; }}
QCheckBox::indicator:checked {{ background-color: {acento}; }}
QRadioButton::indicator:checked {{ background-color: {acento}; }}
QTextEdit {{ font-size: 13px; }}
QStatusBar {{ color: {acento}; }}
"""


def brillo(objeto, color, radio=18):
    efecto = QGraphicsDropShadowEffect(objeto)
    efecto.setColor(QColor(color))
    efecto.setBlurRadius(radio)
    efecto.setOffset(0, 0)
    objeto.setGraphicsEffect(efecto)
    return efecto


class DetalleDialog(QDialog):
    confirmado = pyqtSignal(str)

    def __init__(self, parent=None, registro=None, acento="#00f0ff"):
        super().__init__(parent)
        self.registro = registro
        self.setWindowTitle("{} :: detalle del registro".format(TITULO))
        self.setModal(True)
        self.setMinimumWidth(430)
        self.setStyleSheet(TEMA.format(acento=acento))

        encabezado = QLabel("FICHA DEL ESTUDIANTE")
        encabezado.setFont(QFont("Consolas", 14, QFont.Bold))
        encabezado.setAlignment(Qt.AlignCenter)
        brillo(encabezado, acento, 22)

        self.txt_detalle = QTextEdit()
        self.txt_detalle.setReadOnly(True)
        self.txt_detalle.setFixedHeight(130)

        self.cmb_carrera = QComboBox()
        self.cmb_carrera.addItems(CARRERAS)

        self.rb_activo = QRadioButton("Activo")
        self.rb_inactivo = QRadioButton("Inactivo")
        self.rb_activo.setChecked(True)

        self.ck_becado = QCheckBox("Becado")
        self.ck_repetidor = QCheckBox("Repetidor")

        estado = QWidget()
        fila_estado = QHBoxLayout(estado)
        fila_estado.setContentsMargins(0, 0, 0, 0)
        fila_estado.addWidget(self.rb_activo)
        fila_estado.addWidget(self.rb_inactivo)
        fila_estado.addStretch()

        marcas = QWidget()
        fila_marcas = QHBoxLayout(marcas)
        fila_marcas.setContentsMargins(0, 0, 0, 0)
        fila_marcas.addWidget(self.ck_becado)
        fila_marcas.addWidget(self.ck_repetidor)
        fila_marcas.addStretch()

        if registro:
            estado_texto = "activo" if registro["activo"] else "inactivo"
            self.txt_detalle.setPlainText(
                "Nombre  : {nombre}\n"
                "Cédula  : {cedula}\n"
                "Correo  : {email}\n"
                "Materia : {materia}  ->  Nota: {nota} ({estado_texto})".format(
                    estado_texto=estado_texto, **registro
                )
            )
            indice = self.cmb_carrera.findText(registro["carrera"])
            if indice >= 0:
                self.cmb_carrera.setCurrentIndex(indice)
            if registro["activo"]:
                self.rb_activo.setChecked(True)
            else:
                self.rb_inactivo.setChecked(True)
            self.ck_becado.setChecked(registro["becado"])
            self.ck_repetidor.setChecked(registro["repetidor"])

        formulario = QFormLayout()
        formulario.addRow("Datos:", self.txt_detalle)
        formulario.addRow("Carrera:", self.cmb_carrera)
        formulario.addRow("Estado:", estado)
        formulario.addRow("Marcas:", marcas)

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("CONFIRMAR")
        botones.button(QDialogButtonBox.Cancel).setText("CANCELAR")
        botones.accepted.connect(self.aceptar)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(encabezado)
        layout.addLayout(formulario)
        layout.addWidget(botones)

    def aceptar(self):
        if self.registro is not None:
            self.registro["carrera"] = self.cmb_carrera.currentText()
            self.registro["activo"] = self.rb_activo.isChecked()
            self.registro["becado"] = self.ck_becado.isChecked()
            self.registro["repetidor"] = self.ck_repetidor.isChecked()
            self.confirmado.emit("Ficha de {0} actualizada".format(self.registro["nombre"]))
        self.accept()


class AcercaDeDialog(QDialog):
    def __init__(self, parent=None, acento="#00f0ff"):
        super().__init__(parent)
        self.setWindowTitle("Acerca de {}".format(TITULO))
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet(TEMA.format(acento=acento))

        titulo = QLabel(TITULO)
        titulo.setFont(QFont("Consolas", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        brillo(titulo, acento, 24)

        self.txt_acerca = QTextEdit()
        self.txt_acerca.setReadOnly(True)
        self.txt_acerca.setPlainText(
            "Registro de estudiantes y notas.\n\n"
            "PyQt5: QApplication, QMainWindow, QWidget, QDialog,\n"
            "QLabel, QPushButton, QLineEdit, QTextEdit,\n"
            "QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,\n"
            "QCheckBox, QRadioButton, QComboBox, QAction, menus,\n"
            "eventos, señales/slots y QTimer.\n\n"
            "Fue echo por el echicero"
        )

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(self.reject)
        botones.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(titulo)
        layout.addWidget(self.txt_acerca)
        layout.addWidget(botones)


class VentanaPrincipal(QMainWindow):
    notificado = pyqtSignal(str)
    registro_agregado = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(TITULO)
        self.resize(980, 740)

        self.acento = ACENTOS[0]
        self.registros = []
        self.visibles = []
        self.parpadeo = False
        self.cargar_datos()

        self.crear_menus()
        self.crear_ui()
        self.aplicar_tema(self.acento)

        self.notificado.connect(self.mostrar_notificacion)
        self.registro_agregado.connect(self.al_agregar_registro)

        self.actualizar_resumen()
        self.mostrar_registros()

        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.tick_reloj)
        self.timer_reloj.start(1000)

        self.timer_guardado = QTimer(self)
        self.timer_guardado.timeout.connect(self.guardado_automatico)
        self.timer_guardado.start(30000)

        self.notificado.emit("{} listo. Usa el menú Archivo o F1 para ver los atajos.".format(TITULO))

    def crear_ui(self):
        contenedor = QWidget()
        self.setCentralWidget(contenedor)

        raiz = QVBoxLayout(contenedor)

        cabecera = QHBoxLayout()
        self.lbl_titulo = QLabel(TITULO)
        self.lbl_titulo.setFont(QFont("Consolas", 22, QFont.Bold))
        brillo(self.lbl_titulo, self.acento, 26)

        self.lbl_reloj = QLabel("--:--:--")
        self.lbl_reloj.setFont(QFont("Consolas", 16, QFont.Bold))
        self.lbl_reloj.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.lbl_vivo = QLabel("EN VIVO")
        self.lbl_vivo.setFont(QFont("Consolas", 11, QFont.Bold))
        self.lbl_vivo.setAlignment(Qt.AlignCenter)

        cabecera.addWidget(self.lbl_titulo, 1)
        cabecera.addWidget(self.lbl_vivo)
        cabecera.addWidget(self.lbl_reloj)
        raiz.addLayout(cabecera)

        self.lbl_subtitulo = QLabel("Usa la barra de menús :: F1 ayuda :: C cambia la luz")
        self.lbl_subtitulo.setAlignment(Qt.AlignCenter)
        raiz.addWidget(self.lbl_subtitulo)

        panel = QWidget()
        raiz.addWidget(panel)
        fila_panel = QHBoxLayout(panel)
        self.crear_panel_datos(fila_panel)
        self.crear_panel_filtros(fila_panel)

        raiz.addLayout(self.crear_barra_busqueda())

        self.lbl_contador = QLabel("Registros guardados: 0")
        self.lbl_contador.setFont(QFont("Consolas", 11, QFont.Bold))
        raiz.addWidget(self.lbl_contador)

        self.txt_lista = QTextEdit()
        self.txt_lista.setReadOnly(True)
        raiz.addWidget(self.txt_lista)

        pie = QLabel("Fue echo por el echicero")
        pie.setAlignment(Qt.AlignCenter)
        raiz.addWidget(pie)

        self.lbl_estado = QLabel("Esperando datos...")
        self.lbl_estado.setWordWrap(True)
        raiz.addWidget(self.lbl_estado)

    def crear_menus(self):
        barra = self.menuBar()
        barra.setStyleSheet(TEMA.format(acento=self.acento))

        self.acciones = {}

        archivo = barra.addMenu("&Archivo")
        accion_nuevo = QAction("&Nuevo registro", self)
        accion_nuevo.setShortcut(QKeySequence.New)
        accion_nuevo.setStatusTip("Limpia el formulario para capturar un registro nuevo")
        accion_nuevo.triggered.connect(self.limpiar_formulario)
        archivo.addAction(accion_nuevo)

        accion_guardar = QAction("&Guardar", self)
        accion_guardar.setShortcut(QKeySequence.Save)
        accion_guardar.setStatusTip("Guarda los registros en el disco")
        accion_guardar.triggered.connect(self.guardar_datos)
        archivo.addAction(accion_guardar)

        accion_exportar = QAction("&Exportar reporte...", self)
        accion_exportar.setShortcut("Ctrl+E")
        accion_exportar.setStatusTip("Exporta los registros a un archivo de texto")
        accion_exportar.triggered.connect(self.exportar)
        archivo.addAction(accion_exportar)

        archivo.addSeparator()

        accion_salir = QAction("&Salir", self)
        accion_salir.setShortcut("Ctrl+Q")
        accion_salir.setStatusTip("Cierra el sistema")
        accion_salir.triggered.connect(self.close)
        archivo.addAction(accion_salir)

        edicion = barra.addMenu("&Edición")
        accion_limpiar = QAction("&Limpiar formulario", self)
        accion_limpiar.setShortcut("Esc")
        accion_limpiar.setStatusTip("Borra los campos del formulario")
        accion_limpiar.triggered.connect(self.limpiar_formulario)
        edicion.addAction(accion_limpiar)

        accion_detalle = QAction("Ver / editar &detalle...", self)
        accion_detalle.setShortcut("F5")
        accion_detalle.setStatusTip("Abre la ficha del registro seleccionado")
        accion_detalle.triggered.connect(self.ver_detalle)
        edicion.addAction(accion_detalle)

        accion_eliminar = QAction("&Eliminar último registro", self)
        accion_eliminar.setShortcut("Ctrl+Del")
        accion_eliminar.setStatusTip("Borra el registro más reciente")
        accion_eliminar.triggered.connect(self.eliminar_ultimo)
        edicion.addAction(accion_eliminar)

        edicion.addSeparator()

        accion_color = QAction("Cambiar &luz neon", self)
        accion_color.setShortcut("C")
        accion_color.setStatusTip("Cambia el color de acento de la interfaz")
        accion_color.triggered.connect(self.cambiar_color)
        edicion.addAction(accion_color)

        registros = barra.addMenu("&Registros")
        accion_registrar = QAction("&Registrar estudiante", self)
        accion_registrar.setShortcut("Ctrl+R")
        accion_registrar.setStatusTip("Agrega el estudiante que está en el formulario")
        accion_registrar.triggered.connect(self.registrar)
        registros.addAction(accion_registrar)

        menu_orden = registros.addMenu("Ordenar por")
        grupo_orden = QActionGroup(self)
        grupo_orden.setExclusive(True)
        self.rb_por_nombre = QRadioButton("Nombre")
        self.rb_por_nota = QRadioButton("Nota (mayor a menor)")
        self.rb_por_carrera = QRadioButton("Carrera")
        self.rb_por_nombre.setChecked(True)

        for indice, (titulo, boton, atajo) in enumerate(
            [
                ("Nombre", self.rb_por_nombre, "Ctrl+1"),
                ("Nota (mayor a menor)", self.rb_por_nota, "Ctrl+2"),
                ("Carrera", self.rb_por_carrera, "Ctrl+3"),
            ]
        ):
            accion = QAction(titulo, self, checkable=True)
            accion.setShortcut(atajo)
            accion.setChecked(boton.isChecked())
            accion.triggered.connect(self.al_cambiar_orden_menu)
            grupo_orden.addAction(accion)
            menu_orden.addAction(accion)
            self.acciones["orden_{0}".format(indice)] = accion

        registros.addSeparator()

        accion_borrar = QAction("Borrar &todo", self)
        accion_borrar.setShortcut("Ctrl+Shift+B")
        accion_borrar.setStatusTip("Elimina todos los registros guardados")
        accion_borrar.triggered.connect(self.borrar_todo)
        registros.addAction(accion_borrar)

        ver = barra.addMenu("&Ver")
        menu_filtros = ver.addMenu("Filtros")
        self.filtros = {
            "aprobados": QCheckBox("Solo aprobados"),
            "reprobados": QCheckBox("Solo reprobados"),
            "activos": QCheckBox("Solo activos"),
            "becados": QCheckBox("Solo becados"),
        }

        for clave, casilla in self.filtros.items():
            accion = QAction(casilla.text(), self, checkable=True)
            accion.setStatusTip("Muestra solo los registros que cumplen: {0}".format(clave))
            accion.triggered.connect(
                lambda _marcado=False, casilla=casilla: self.alternar_filtro(casilla)
            )
            menu_filtros.addAction(accion)
            self.acciones["filtro_{0}".format(clave)] = accion

        menu_nota = ver.addMenu("Nota mínima")
        grupo_nota = QActionGroup(self)
        grupo_nota.setExclusive(True)
        for valor in [0, 50, 70, 90]:
            accion = QAction("Todas" if valor == 0 else str(valor), self, checkable=True)
            accion.setData(valor)
            accion.setChecked(valor == 0)
            accion.triggered.connect(
                lambda _marcado=False, accion=accion: self.al_cambiar_nota_minima(accion)
            )
            grupo_nota.addAction(accion)
            menu_nota.addAction(accion)
            self.acciones["nota_{0}".format(valor)] = accion

        ayuda = barra.addMenu("A&yuda")
        accion_atajos = QAction("&Atajos de teclado...", self)
        accion_atajos.setShortcut("F1")
        accion_atajos.setStatusTip("Muestra la lista de atajos del sistema")
        accion_atajos.triggered.connect(self.mostrar_atajos)
        ayuda.addAction(accion_atajos)

        accion_acerca = QAction("&Acerca de...", self)
        accion_acerca.setStatusTip("Información del sistema")
        accion_acerca.triggered.connect(self.mostrar_acerca_de)
        ayuda.addAction(accion_acerca)

        for accion in self.findChildren(QAction):
            accion.hovered.connect(self.al_hover_accion)

    def al_hover_accion(self, accion):
        self.statusBar().showMessage(accion.statusTip() or accion.text())

    def al_cambiar_orden_menu(self):
        indice = self.menu_orden_activa()
        if indice == 1:
            self.rb_por_nota.setChecked(True)
        elif indice == 2:
            self.rb_por_carrera.setChecked(True)
        else:
            self.rb_por_nombre.setChecked(True)
        self.ordenar()

    def menu_orden_activa(self):
        for indice in range(3):
            if self.acciones["orden_{0}".format(indice)].isChecked():
                return indice
        return 0

    def al_cambiar_nota_minima(self, accion):
        valor = accion.data()
        texto = "Todas" if valor == 0 else str(valor)
        indice = self.cmb_nota_min.findText(texto)
        if indice >= 0:
            self.cmb_nota_min.setCurrentIndex(indice)
        self.mostrar_registros()

    def mostrar_atajos(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Atajos de teclado")
        dialogo.setModal(True)
        dialogo.setMinimumWidth(420)
        dialogo.setStyleSheet(TEMA.format(acento=self.acento))

        lista = QTextEdit()
        lista.setReadOnly(True)
        lista.setPlainText(
            "Ctrl+N     Nuevo registro\n"
            "Ctrl+R     Registrar estudiante\n"
            "Ctrl+S     Guardar\n"
            "Ctrl+E     Exportar reporte\n"
            "Ctrl+Del   Eliminar último registro\n"
            "Ctrl+1/2/3 Ordenar por nombre / nota / carrera\n"
            "F1         Esta ayuda\n"
            "F5         Ver o editar detalle\n"
            "Esc        Limpiar formulario\n"
            "C          Cambiar luz neon\n"
            "Supr/Inf   Subir o bajar la nota (rueda del mouse)\n"
            "Doble clic Ordena por nota"
        )

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(dialogo.reject)
        botones.accepted.connect(dialogo.accept)

        layout = QVBoxLayout(dialogo)
        layout.addWidget(QLabel("Atajos disponibles"))
        layout.addWidget(lista)
        layout.addWidget(botones)
        dialogo.exec_()

    def mostrar_acerca_de(self):
        dialogo = AcercaDeDialog(self, self.acento)
        dialogo.exec_()

    def crear_panel_datos(self, layout_padre):
        grupo = QGroupBox("DATOS DEL ESTUDIANTE")
        layout = QVBoxLayout(grupo)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre completo")
        self.txt_cedula = QLineEdit()
        self.txt_cedula.setPlaceholderText("Cédula / Matrícula")
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("Correo electrónico")
        self.txt_materia = QLineEdit()
        self.txt_materia.setPlaceholderText("Materia")
        self.txt_nota = QLineEdit()
        self.txt_nota.setPlaceholderText("Nota de 0 a 100")
        self.txt_nota.setValidator(QDoubleValidator(0.0, 100.0, 2, self))

        self.cmb_carrera = QComboBox()
        self.cmb_carrera.addItems(CARRERAS)
        self.cmb_carrera.setEditable(True)

        self.rb_activo = QRadioButton("Activo")
        self.rb_inactivo = QRadioButton("Inactivo")
        self.rb_activo.setChecked(True)

        self.ck_becado = QCheckBox("Becado")
        self.ck_repetidor = QCheckBox("Repetidor")

        estado = QWidget()
        fila_estado = QHBoxLayout(estado)
        fila_estado.setContentsMargins(0, 0, 0, 0)
        fila_estado.addWidget(self.rb_activo)
        fila_estado.addWidget(self.rb_inactivo)
        fila_estado.addStretch()

        marcas = QWidget()
        fila_marcas = QHBoxLayout(marcas)
        fila_marcas.setContentsMargins(0, 0, 0, 0)
        fila_marcas.addWidget(self.ck_becado)
        fila_marcas.addWidget(self.ck_repetidor)
        fila_marcas.addStretch()

        formulario = QFormLayout()
        formulario.addRow("Nombre:", self.txt_nombre)
        formulario.addRow("Cédula:", self.txt_cedula)
        formulario.addRow("Carrera:", self.cmb_carrera)
        formulario.addRow("Correo:", self.txt_email)
        formulario.addRow("Materia:", self.txt_materia)
        formulario.addRow("Nota:", self.txt_nota)
        formulario.addRow("Estado:", estado)
        formulario.addRow("Marcas:", marcas)
        layout.addLayout(formulario)

        self.btn_registrar = QPushButton("REGISTRAR")
        self.btn_limpiar = QPushButton("LIMPIAR")
        self.btn_detalle = QPushButton("VER DETALLE")
        self.btn_ultimo = QPushButton("ELIMINAR ÚLTIMO")
        self.btn_ordenar = QPushButton("ORDENAR")
        self.btn_exportar = QPushButton("EXPORTAR")
        self.btn_borrar = QPushButton("BORRAR TODO")

        for boton in (self.btn_registrar, self.btn_detalle):
            brillo(boton, self.acento, 16)

        self.btn_registrar.clicked.connect(self.registrar)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        self.btn_detalle.clicked.connect(self.ver_detalle)
        self.btn_ultimo.clicked.connect(self.eliminar_ultimo)
        self.btn_ordenar.clicked.connect(self.ordenar)
        self.btn_exportar.clicked.connect(self.exportar)
        self.btn_borrar.clicked.connect(self.borrar_todo)

        primera = QHBoxLayout()
        primera.addWidget(self.btn_registrar)
        primera.addWidget(self.btn_limpiar)
        primera.addWidget(self.btn_detalle)
        layout.addLayout(primera)

        segunda = QHBoxLayout()
        segunda.addWidget(self.btn_ultimo)
        segunda.addWidget(self.btn_ordenar)
        segunda.addWidget(self.btn_exportar)
        segunda.addWidget(self.btn_borrar)
        layout.addLayout(segunda)

        layout_padre.addWidget(grupo, 3)

    def crear_panel_filtros(self, layout_padre):
        grupo = QGroupBox("FILTROS Y RESUMEN")
        layout = QVBoxLayout(grupo)

        for casilla in self.filtros.values():
            casilla.stateChanged.connect(self.al_cambiar_filtro)
            layout.addWidget(casilla)

        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        layout.addWidget(separador)

        etiqueta_orden = QLabel("Ordenar por:")
        etiqueta_orden.setFont(QFont("Consolas", 10, QFont.Bold))
        layout.addWidget(etiqueta_orden)

        for boton in (self.rb_por_nombre, self.rb_por_nota, self.rb_por_carrera):
            boton.toggled.connect(self.al_cambiar_orden)
            layout.addWidget(boton)

        self.lbl_total = QLabel("0")
        self.lbl_aprobados = QLabel("0")
        self.lbl_reprobados = QLabel("0")
        self.lbl_promedio = QLabel("0.00")
        self.lbl_becados = QLabel("0")
        self.lbl_activos = QLabel("0")

        cuadricula = QGridLayout()
        titulos = ["Total", "Aprobados", "Reprobados", "Promedio", "Becados", "Activos"]
        valores = [
            self.lbl_total,
            self.lbl_aprobados,
            self.lbl_reprobados,
            self.lbl_promedio,
            self.lbl_becados,
            self.lbl_activos,
        ]
        for indice, (titulo, valor) in enumerate(zip(titulos, valores)):
            valor.setAlignment(Qt.AlignCenter)
            valor.setFont(QFont("Consolas", 14, QFont.Bold))
            brillo(valor, self.acento, 14)
            cuadricula.addWidget(QLabel(titulo), indice // 2, (indice % 2) * 2)
            cuadricula.addWidget(valor, indice // 2, (indice % 2) * 2 + 1)
        cuadricula.setVerticalSpacing(8)
        layout.addLayout(cuadricula)

        layout.addStretch()
        layout_padre.addWidget(grupo, 2)

    def crear_barra_busqueda(self):
        barra = QHBoxLayout()

        self.cmb_campo = QComboBox()
        self.cmb_campo.addItems(["Nombre", "Cédula", "Carrera", "Correo", "Materia", "Nota"])
        self.cmb_campo.setFixedWidth(130)

        self.txt_filtro = QLineEdit()
        self.txt_filtro.setPlaceholderText("Buscar...")
        self.txt_filtro.textChanged.connect(self.al_escribir_busqueda)

        self.cmb_nota_min = QComboBox()
        self.cmb_nota_min.addItems(["Todas"] + [str(n) for n in range(0, 101, 10)])

        self.cmb_campo.currentIndexChanged.connect(self.al_cambiar_combo)
        self.cmb_nota_min.currentIndexChanged.connect(self.al_cambiar_combo)

        barra.addWidget(QLabel("Campo:"))
        barra.addWidget(self.cmb_campo)
        barra.addWidget(self.txt_filtro, 1)
        barra.addWidget(QLabel("Nota mínima:"))
        barra.addWidget(self.cmb_nota_min)
        return barra

    def aplicar_tema(self, acento):
        self.acento = acento
        self.setStyleSheet(TEMA.format(acento=acento))
        self.menuBar().setStyleSheet(TEMA.format(acento=acento))
        paleta = QPalette()
        paleta.setColor(QPalette.Window, QColor("#05060f"))
        paleta.setColor(QPalette.WindowText, QColor(acento))
        paleta.setColor(QPalette.Base, QColor("#0b0f1e"))
        paleta.setColor(QPalette.Text, QColor(acento))
        paleta.setColor(QPalette.Highlight, QColor(acento))
        paleta.setColor(QPalette.HighlightedText, QColor("#05060f"))
        self.setPalette(paleta)

        for etiqueta in (
            self.lbl_titulo,
            self.lbl_total,
            self.lbl_aprobados,
            self.lbl_reprobados,
            self.lbl_promedio,
            self.lbl_becados,
            self.lbl_activos,
            self.btn_registrar,
            self.btn_detalle,
        ):
            brillo(etiqueta, acento)

    def alternar_filtro(self, casilla):
        casilla.setChecked(not casilla.isChecked())

    def al_escribir_busqueda(self, _texto):
        self.mostrar_registros()

    def al_cambiar_combo(self, _indice):
        self.mostrar_registros()

    def al_cambiar_filtro(self, _estado):
        for clave, casilla in self.filtros.items():
            self.acciones["filtro_{0}".format(clave)].setChecked(casilla.isChecked())
        self.mostrar_registros()
        self.notificado.emit("Filtro actualizado")

    def al_cambiar_orden(self, _marcado):
        indice = self.menu_orden_activa()
        activo = 0 if self.rb_por_nombre.isChecked() else (1 if self.rb_por_nota.isChecked() else 2)
        if activo != indice:
            self.acciones["orden_{0}".format(activo)].setChecked(True)
        self.ordenar()

    def al_agregar_registro(self, registro):
        self.notificado.emit("Registrado: {0}".format(registro["nombre"]))
        self.statusBar().showMessage("Total: {0}".format(len(self.registros)), 3000)

    def mostrar_notificacion(self, mensaje):
        self.lbl_estado.setText(mensaje)

    def tick_reloj(self):
        self.lbl_reloj.setText(datetime.now().strftime("%H:%M:%S"))
        self.parpadeo = not self.parpadeo
        self.lbl_vivo.setStyleSheet("color: {0};".format(self.acento if self.parpadeo else "#1c2233"))

    def guardado_automatico(self):
        self.guardar_datos()
        self.notificado.emit("Guardado automático {0}".format(datetime.now().strftime("%H:%M:%S")))

    def cambiar_color(self):
        siguiente = ACENTOS[(ACENTOS.index(self.acento) + 1) % len(ACENTOS)]
        self.aplicar_tema(siguiente)
        self.notificado.emit("Luz neon cambiada a {0}".format(siguiente))

    def guardar_datos(self):
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
            json.dump(self.registros, archivo, indent=2, ensure_ascii=False)

    def cargar_datos(self):
        if not os.path.exists(ARCHIVO_DATOS):
            return
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
                self.registros = json.load(archivo)
        except (json.JSONDecodeError, OSError):
            self.registros = []

    def leer_formulario(self):
        try:
            nota = float(self.txt_nota.text().strip() or 0)
        except ValueError:
            return None
        if not 0 <= nota <= 100:
            return None
        return {
            "nombre": self.txt_nombre.text().strip(),
            "cedula": self.txt_cedula.text().strip(),
            "carrera": self.cmb_carrera.currentText().strip(),
            "email": self.txt_email.text().strip(),
            "materia": self.txt_materia.text().strip(),
            "nota": nota,
            "activo": self.rb_activo.isChecked(),
            "becado": self.ck_becado.isChecked(),
            "repetidor": self.ck_repetidor.isChecked(),
        }

    def registrar(self):
        registro = self.leer_formulario()
        if registro is None:
            self.notificado.emit("La nota debe estar entre 0 y 100")
            QMessageBox.warning(self, "Datos inválidos", "La nota debe estar entre 0 y 100.")
            return

        if not registro["nombre"] or not registro["cedula"] or not registro["materia"]:
            self.notificado.emit("Faltan nombre, cédula o materia")
            QMessageBox.warning(
                self, "Datos incompletos", "Nombre, cédula y materia son obligatorios."
            )
            return

        if any(r["cedula"] == registro["cedula"] for r in self.registros):
            self.notificado.emit("Cédula duplicada: {0}".format(registro["cedula"]))
            QMessageBox.warning(self, "Duplicado", "Ya existe un registro con esa cédula.")
            return

        self.registros.append(registro)
        self.registro_agregado.emit(registro)
        self.guardar_datos()
        self.actualizar_resumen()
        self.mostrar_registros()
        self.limpiar_formulario()

    def eliminar_ultimo(self):
        if not self.registros:
            QMessageBox.information(self, "Aviso", "No hay registros para eliminar.")
            return

        respuesta = QMessageBox.question(
            self, "Eliminar", "¿Eliminar el último registro de la lista?"
        )
        if respuesta == QMessageBox.Yes:
            eliminado = self.registros.pop()
            self.guardar_datos()
            self.actualizar_resumen()
            self.mostrar_registros()
            self.notificado.emit("Eliminado: {0}".format(eliminado["nombre"]))

    def ver_detalle(self):
        registro = self.registro_seleccionado()
        if registro is None:
            QMessageBox.information(self, "Aviso", "No hay ningún registro seleccionado.")
            return

        dialogo = DetalleDialog(self, registro, self.acento)
        dialogo.confirmado.connect(self.mostrar_notificacion)
        if dialogo.exec_() == QDialog.Accepted:
            self.guardar_datos()
            self.actualizar_resumen()
            self.mostrar_registros()

    def registro_seleccionado(self):
        if not self.visibles:
            return self.registros[-1] if self.registros else None

        seleccion = self.txt_lista.textCursor().selectionStart()
        if not seleccion:
            return self.visibles[-1][1]

        linea = self.txt_lista.toPlainText()[:seleccion].count("\n")
        return self.visibles[min(linea, len(self.visibles) - 1)][1]

    def limpiar_formulario(self):
        for campo in (
            self.txt_nombre,
            self.txt_cedula,
            self.txt_email,
            self.txt_materia,
            self.txt_nota,
        ):
            campo.clear()
        self.cmb_carrera.setCurrentIndex(0)
        self.rb_activo.setChecked(True)
        self.ck_becado.setChecked(False)
        self.ck_repetidor.setChecked(False)
        self.txt_nombre.setFocus()

    def borrar_todo(self):
        if not self.registros:
            QMessageBox.information(self, "Aviso", "No hay registros para borrar.")
            return

        respuesta = QMessageBox.question(
            self, "Borrar todo", "¿Deseas borrar todos los registros guardados?"
        )
        if respuesta == QMessageBox.Yes:
            self.registros = []
            self.guardar_datos()
            self.actualizar_resumen()
            self.mostrar_registros()
            self.notificado.emit("Todos los registros fueron borrados")

    def ordenar(self):
        if not self.registros:
            return

        def clave(registro):
            if self.rb_por_nota.isChecked():
                return -registro["nota"]
            if self.rb_por_carrera.isChecked():
                return registro["carrera"].lower()
            return registro["nombre"].lower()

        self.registros.sort(key=clave)
        self.guardar_datos()
        self.mostrar_registros()

    def exportar(self):
        if not self.registros:
            QMessageBox.information(self, "Aviso", "No hay registros para exportar.")
            return

        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro6_reporte.txt")
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write("{} - REPORTE\n".format(TITULO))
            archivo.write("Fue echo por el echicero\n")
            archivo.write("=" * 60 + "\n")
            for posicion, registro in enumerate(self.registros, start=1):
                marcas = []
                if registro["becado"]:
                    marcas.append("becado")
                if registro["repetidor"]:
                    marcas.append("repetidor")
                archivo.write(
                    "{0}. {1} ({2}) | {3} | {4} | Nota: {5:.1f} | {6} | {7}\n".format(
                        posicion,
                        registro["nombre"],
                        registro["cedula"],
                        registro["carrera"],
                        registro["materia"],
                        registro["nota"],
                        "activo" if registro["activo"] else "inactivo",
                        ", ".join(marcas) if marcas else "sin marcas",
                    )
                )
            notas = [r["nota"] for r in self.registros]
            archivo.write("-" * 60 + "\n")
            archivo.write(
                "Total: {0} | Aprobados: {1} | Reprobados: {2} | Promedio: {3:.2f}\n".format(
                    len(notas),
                    sum(1 for n in notas if n >= 50),
                    sum(1 for n in notas if n < 50),
                    sum(notas) / len(notas),
                )
            )

        QMessageBox.information(self, "Exportar", "Reporte guardado en:\n{0}".format(ruta))
        self.notificado.emit("Reporte exportado en {0}".format(ruta))

    def actualizar_resumen(self):
        notas = [r["nota"] for r in self.registros]
        self.lbl_total.setText(str(len(notas)))
        self.lbl_aprobados.setText(str(sum(1 for n in notas if n >= 50)))
        self.lbl_reprobados.setText(str(sum(1 for n in notas if n < 50)))
        self.lbl_promedio.setText("{0:.2f}".format(sum(notas) / len(notas)) if notas else "0.00")
        self.lbl_becados.setText(str(sum(1 for r in self.registros if r["becado"])))
        self.lbl_activos.setText(str(sum(1 for r in self.registros if r["activo"])))

    def mostrar_registros(self, texto_filtro=None):
        if texto_filtro is None:
            texto_filtro = self.txt_filtro.text().strip().lower()

        campo = self.cmb_campo.currentText()
        indice_minimo = self.cmb_nota_min.currentIndex()
        nota_minima = 0.0 if indice_minimo == 0 else float(self.cmb_nota_min.currentText())

        self.txt_lista.clear()
        self.visibles = []
        lineas = []

        for posicion, registro in enumerate(self.registros, start=1):
            if self.filtros["aprobados"].isChecked() and registro["nota"] < 50:
                continue
            if self.filtros["reprobados"].isChecked() and registro["nota"] >= 50:
                continue
            if self.filtros["activos"].isChecked() and not registro["activo"]:
                continue
            if self.filtros["becados"].isChecked() and not registro["becado"]:
                continue
            if registro["nota"] < nota_minima:
                continue

            if texto_filtro:
                if campo == "Nota":
                    coincide = texto_filtro in "{0:.1f}".format(registro["nota"])
                else:
                    coincide = texto_filtro in str(registro[campo.lower()]).lower()
                if not coincide:
                    continue

            marcas = []
            if registro["becado"]:
                marcas.append("B")
            if registro["repetidor"]:
                marcas.append("R")
            linea = (
                "{pos}. {nombre} | {cedula} | {carrera} | {materia} | Nota: {nota:.1f} "
                "{resultado} [{estado}]{marcas}"
            ).format(
                pos=posicion,
                resultado="APROBADO" if registro["nota"] >= 50 else "REPROBADO",
                estado="A" if registro["activo"] else "I",
                marcas=(" " + "/".join(marcas)) if marcas else "",
                **registro
            )
            lineas.append(linea)
            self.visibles.append((posicion, registro))

        if not lineas:
            self.txt_lista.setPlainText("No hay registros que cumplan los filtros.")
        else:
            self.txt_lista.setPlainText("\n".join(lineas))

        self.lbl_contador.setText(
            "Registros guardados: {0} | Mostrados: {1}".format(
                len(self.registros), len(self.visibles)
            )
        )

    def mousePressEvent(self, evento):
        if evento.type() == QEvent.MouseButtonPress:
            if evento.button() == Qt.LeftButton and not self.hay_dialogo_abierto():
                self.cambiar_color()
        super().mousePressEvent(evento)

    def mouseDoubleClickEvent(self, evento):
        self.notificado.emit("Doble clic: reordenando por nota")
        self.acciones["orden_1"].setChecked(True)
        self.al_cambiar_orden_menu()
        super().mouseDoubleClickEvent(evento)

    def wheelEvent(self, evento):
        registro = self.registro_seleccionado()
        if registro is None:
            return
        paso = 1.0 if evento.angleDelta().y() > 0 else -1.0
        registro["nota"] = min(100.0, max(0.0, registro["nota"] + paso))
        self.guardar_datos()
        self.actualizar_resumen()
        self.mostrar_registros()
        self.notificado.emit("Nota de {0}: {1:.1f}".format(registro["nombre"], registro["nota"]))

    def keyPressEvent(self, evento):
        if self.hay_dialogo_abierto():
            super().keyPressEvent(evento)
            return

        if evento.key() == Qt.Key_C and not self.hay_tecla_de_texto():
            self.cambiar_color()
        else:
            super().keyPressEvent(evento)

    def hay_dialogo_abierto(self):
        return QApplication.activeModalWidget() is not None

    def hay_tecla_de_texto(self):
        return isinstance(QApplication.focusWidget(), (QLineEdit, QTextEdit))

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self.lbl_subtitulo.setText(
            "{0}  ::  {1}x{2}  ::  F1 ayuda  ::  C cambia la luz  ::  doble clic ordena por nota".format(
                TITULO, self.width(), self.height()
            )
        )

    def closeEvent(self, evento):
        self.guardar_datos()
        self.timer_reloj.stop()
        self.timer_guardado.stop()
        self.notificado.emit("Sesión cerrada. Datos guardados.")
        super().closeEvent(evento)


def main():
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
