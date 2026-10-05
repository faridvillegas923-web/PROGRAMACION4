import json
import os
import sys
from datetime import datetime

from PyQt5.QtCore import QEvent, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QDoubleValidator, QFont, QKeySequence, QPalette
from PyQt5.QtWidgets import (
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

ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro5_datos.json")

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
QLineEdit, QTextEdit, QComboBox {{
    background-color: #0b0f1e;
    border: 1px solid {acento};
    border-radius: 4px;
    padding: 5px;
    selection-background-color: {acento};
    selection-color: #05060f;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border: 2px solid {acento};
}}
QPushButton {{
    background-color: #0b0f1e;
    border: 1px solid {acento};
    border-radius: 4px;
    padding: 7px 12px;
    color: {acento};
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {acento};
    color: #05060f;
}}
QPushButton:pressed {{
    background-color: #ffffff;
    color: {acento};
}}
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
QCheckBox, QRadioButton {{
    spacing: 8px;
    color: {acento};
}}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 15px;
    height: 15px;
    border: 1px solid {acento};
    background-color: #0b0f1e;
}}
QRadioButton::indicator {{ border-radius: 8px; }}
QCheckBox::indicator:checked {{ background-color: {acento}; }}
QRadioButton::indicator:checked {{ background-color: {acento}; }}
QTextEdit {{
    font-size: 13px;
}}
QStatusBar {{ color: {acento}; }}
"""


def brillo(objeto, color, radio=18):
    efecto = QGraphicsDropShadowEffect(objeto)
    efecto.setColor(QColor(color))
    efecto.setBlurRadius(radio)
    efecto.setOffset(0, 0)
    objeto.setGraphicsEffect(efecto)
    return efecto


class NeonDialog(QDialog):
    confirmado = pyqtSignal(str)

    def __init__(self, parent=None, registro=None, acento="#00f0ff"):
        super().__init__(parent)
        self.registro = registro
        self.setWindowTitle("NEON :: detalle del registro")
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

        self.lbl_pie = QLabel("F5 ver detalle   |   ESC cerrar")
        self.lbl_pie.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(encabezado)
        layout.addLayout(formulario)
        layout.addWidget(self.lbl_pie)
        layout.addWidget(botones)

    def aceptar(self):
        if self.registro is not None:
            self.registro["carrera"] = self.cmb_carrera.currentText()
            self.registro["activo"] = self.rb_activo.isChecked()
            self.registro["becado"] = self.ck_becado.isChecked()
            self.registro["repetidor"] = self.ck_repetidor.isChecked()
            self.confirmado.emit("Ficha de {0} actualizada".format(self.registro["nombre"]))
        self.accept()


class VentanaPrincipal(QMainWindow):
    notificado = pyqtSignal(str)
    registro_agregado = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEON REGISTRY :: sistema de registro de estudiantes y notas")
        self.resize(960, 720)

        self.acento = ACENTOS[0]
        self.registros = []
        self.visibles = []
        self.parpadeo = False
        self.cargar_datos()

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

        QApplication.instance().installEventFilter(self)

        self.notificado.emit("Sistema NEON iniciado. Ctrl+S guarda, F5 ver detalle.")

    def crear_ui(self):
        contenedor = QWidget()
        self.setCentralWidget(contenedor)

        raiz = QVBoxLayout(contenedor)

        cabecera = QHBoxLayout()
        self.lbl_titulo = QLabel("NEON REGISTRY")
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

        self.lbl_subtitulo = QLabel("Registro de estudiantes y notas  ::  Ctrl+N nuevo  Ctrl+S guardar  F5 detalle  ESC limpiar")
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
        self.lbl_pie = pie
        raiz.addWidget(pie)

        self.lbl_estado = QLabel("Esperando datos...")
        self.lbl_estado.setWordWrap(True)
        raiz.addWidget(self.lbl_estado)

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
        self.btn_ultimo = QPushButton("ELIMINAR ÚLTIMO")
        self.btn_detalle = QPushButton("VER DETALLE")
        self.btn_color = QPushButton("CAMBIAR LUZ")
        self.btn_borrar = QPushButton("BORRAR TODO")
        self.btn_ordenar = QPushButton("ORDENAR")
        self.btn_exportar = QPushButton("EXPORTAR")

        for boton in (self.btn_registrar, self.btn_detalle):
            brillo(boton, self.acento, 16)

        self.btn_registrar.clicked.connect(self.registrar)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        self.btn_ultimo.clicked.connect(self.eliminar_ultimo)
        self.btn_detalle.clicked.connect(self.ver_detalle)
        self.btn_color.clicked.connect(self.cambiar_color)
        self.btn_borrar.clicked.connect(self.borrar_todo)
        self.btn_ordenar.clicked.connect(self.ordenar)
        self.btn_exportar.clicked.connect(self.exportar)

        primera = QHBoxLayout()
        primera.addWidget(self.btn_registrar)
        primera.addWidget(self.btn_limpiar)
        primera.addWidget(self.btn_detalle)
        layout.addLayout(primera)

        segunda = QHBoxLayout()
        segunda.addWidget(self.btn_ultimo)
        segunda.addWidget(self.btn_ordenar)
        segunda.addWidget(self.btn_exportar)
        layout.addLayout(segunda)

        tercera = QHBoxLayout()
        tercera.addWidget(self.btn_color)
        tercera.addWidget(self.btn_borrar)
        layout.addLayout(tercera)

        layout_padre.addWidget(grupo, 3)

    def crear_panel_filtros(self, layout_padre):
        grupo = QGroupBox("FILTROS Y RESUMEN")
        layout = QVBoxLayout(grupo)

        self.ck_solo_aprobados = QCheckBox("Solo aprobados")
        self.ck_solo_reprobados = QCheckBox("Solo reprobados")
        self.ck_solo_activos = QCheckBox("Solo activos")
        self.ck_solo_becados = QCheckBox("Solo becados")

        for casilla in (
            self.ck_solo_aprobados,
            self.ck_solo_reprobados,
            self.ck_solo_activos,
            self.ck_solo_becados,
        ):
            casilla.stateChanged.connect(self.al_cambiar_filtro)
            layout.addWidget(casilla)

        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        layout.addWidget(separador)

        etiqueta_orden = QLabel("Ordenar por:")
        etiqueta_orden.setFont(QFont("Consolas", 10, QFont.Bold))
        layout.addWidget(etiqueta_orden)

        self.rb_por_nombre = QRadioButton("Nombre")
        self.rb_por_nota = QRadioButton("Nota (mayor a menor)")
        self.rb_por_carrera = QRadioButton("Carrera")
        self.rb_por_nombre.setChecked(True)
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

    def al_escribir_busqueda(self, _texto):
        self.mostrar_registros()

    def al_cambiar_combo(self, _indice):
        self.mostrar_registros()

    def al_cambiar_filtro(self, _estado):
        self.mostrar_registros()
        self.notificado.emit("Filtro actualizado")

    def al_cambiar_orden(self, _marcado):
        self.ordenar()

    def al_agregar_registro(self, registro):
        self.notificado.emit("Registrado: {0}".format(registro["nombre"]))
        self.statusBar().showMessage("Total: {0}".format(len(self.registros)), 3000)

    def mostrar_notificacion(self, mensaje):
        self.lbl_estado.setText(mensaje)

    def tick_reloj(self):
        self.lbl_reloj.setText(datetime.now().strftime("%H:%M:%S"))
        self.parpadeo = not self.parpadeo
        color = self.acento if self.parpadeo else "#1c2233"
        self.lbl_vivo.setStyleSheet("color: {0};".format(color))

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

        dialogo = NeonDialog(self, registro, self.acento)
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

        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro5_reporte.txt")
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write("REPORTE NEON - Fue echo por el echicero\n")
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
            if self.ck_solo_aprobados.isChecked() and registro["nota"] < 50:
                continue
            if self.ck_solo_reprobados.isChecked() and registro["nota"] >= 50:
                continue
            if self.ck_solo_activos.isChecked() and not registro["activo"]:
                continue
            if self.ck_solo_becados.isChecked() and not registro["becado"]:
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
        self.rb_por_nota.setChecked(True)
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
        self.notificado.emit(
            "Nota de {0}: {1:.1f}".format(registro["nombre"], registro["nota"])
        )

    def keyPressEvent(self, evento):
        if not self.manejar_atajo(evento):
            super().keyPressEvent(evento)

    def hay_dialogo_abierto(self):
        return QApplication.activeModalWidget() is not None

    def manejar_atajo(self, evento):
        if self.hay_dialogo_abierto():
            return False

        texto = self.hay_tecla_de_texto()

        if evento.matches(QKeySequence.Save):
            self.guardar_datos()
            self.notificado.emit("Guardado manual con Ctrl+S")
            return True
        if evento.matches(QKeySequence.New):
            self.limpiar_formulario()
            self.notificado.emit("Formulario limpio con Ctrl+N")
            return True
        if evento.key() == Qt.Key_F5:
            self.ver_detalle()
            return True
        if evento.key() == Qt.Key_Escape:
            self.limpiar_formulario()
            self.notificado.emit("Formulario limpio con ESC")
            return True
        if not texto and evento.key() == Qt.Key_Delete:
            self.eliminar_ultimo()
            return True
        if not texto and evento.key() == Qt.Key_C:
            self.cambiar_color()
            return True
        return False

    def hay_tecla_de_texto(self):
        return isinstance(QApplication.focusWidget(), (QLineEdit, QTextEdit))

    def eventFilter(self, objeto, evento):
        if evento.type() == QEvent.KeyPress and objeto is not QApplication.activeModalWidget():
            if self.hay_tecla_de_texto() or objeto is self.centralWidget():
                if self.manejar_atajo(evento):
                    return True
        return super().eventFilter(objeto, evento)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self.lbl_subtitulo.setText(
            "Ventana {0}x{1}  ::  Ctrl+N nuevo  Ctrl+S guardar  F5 detalle  "
            "ESC limpiar  SUP/INF nota  C color".format(self.width(), self.height())
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
