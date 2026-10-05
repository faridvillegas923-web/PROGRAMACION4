import json
import math
import os
import sys
from datetime import datetime

from PyQt5.QtCore import QEvent, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QKeySequence
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

ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculadora1_datos.json")
ARCHIVO_REPORTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculadora1_reporte.txt")

TITULO = "CALCULADORA CIENTIFICA"

MODOS = [("deg", "Grados"), ("rad", "Radianes"), ("grad", "Gradianes")]

TEMA = """
QWidget {
    background-color: #f2f2f2;
    color: #1c1c1c;
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}
QMenuBar { background-color: #e4e4e4; border-bottom: 1px solid #bdbdbd; }
QMenuBar::item { padding: 6px 12px; background: transparent; }
QMenuBar::item:selected { background-color: #cdd6e0; }
QMenu { background-color: #f7f7f7; border: 1px solid #bdbdbd; }
QMenu::item { padding: 6px 24px 6px 20px; }
QMenu::item:selected { background-color: #d6e0ee; }
QMenu::separator { height: 1px; background: #cfcfcf; margin: 4px 8px; }
QLineEdit, QTextEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #b4b4b4;
    border-radius: 4px;
    padding: 5px;
    selection-background-color: #c8d8ef;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #7d7d7d; }
QGroupBox {
    border: 1px solid #c6c6c6;
    border-radius: 6px;
    margin-top: 12px;
    background-color: #ededed;
    padding-top: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #3a3a3a;
    font-weight: bold;
}
QPushButton {
    background-color: #ffffff;
    border: 1px solid #b0b0b0;
    border-radius: 4px;
    padding: 8px 6px;
    color: #1c1c1c;
    font-weight: bold;
}
QPushButton:hover { background-color: #eaeaea; border-color: #8f8f8f; }
QPushButton:pressed { background-color: #d6d6d6; }
QPushButton#numero { background-color: #ffffff; font-size: 15px; }
QPushButton#numero:hover { background-color: #f0f4fa; }
QPushButton#operador { background-color: #e4e4e4; }
QPushButton#memoria { background-color: #e8eef7; color: #24476b; }
QPushButton#limpiar { background-color: #f0e6e6; color: #7a2f2f; }
QPushButton#borrar { background-color: #f0e6e6; color: #7a2f2f; }
QPushButton#igual { background-color: #2f6fd0; color: #ffffff; font-size: 16px; }
QPushButton#igual:hover { background-color: #3d7ce0; }
QFrame#marco_pantalla { background-color: #ffffff; border: 1px solid #8f8f8f; border-radius: 4px; }
QLabel#memoria { background-color: #ffffff; color: #5a5a5a; }
QLabel#resultado { background-color: #ffffff; color: #111111; }
QLineEdit#pantalla {
    background-color: #ffffff;
    border: none;
    color: #111111;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 19px;
    font-weight: bold;
    padding: 4px 8px;
}
QLabel#rotulo { color: #4a4a4a; }
QCheckBox, QRadioButton { spacing: 8px; color: #2a2a2a; }
QCheckBox::indicator, QRadioButton::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid #9a9a9a;
    background-color: #ffffff;
}
QRadioButton::indicator { border-radius: 8px; }
QCheckBox::indicator:checked, QRadioButton::indicator:checked { background-color: #2f6fd0; }
QStatusBar { color: #3a3a3a; background-color: #e9e9e9; }
"""

TECLAS = [
    ("MC", "memoria", "Borra la memoria (MC)"),
    ("MR", "memoria", "Recupera la memoria (MR)"),
    ("M+", "memoria", "Suma el resultado a la memoria"),
    ("M-", "memoria", "Resta el resultado de la memoria"),
    ("CE", "limpiar", "Borra solo la entrada actual"),
    ("C", "limpiar", "Borra entrada y resultado"),
    ("(", "operador", "Abre paréntesis"),
    (")", "operador", "Cierra paréntesis"),
    ("%", "operador", "Porcentaje (divide entre 100)"),
    ("÷", "operador", "División"),
    ("x^y", "operador", "Potencia"),
    ("⌫", "borrar", "Borra el último carácter"),
    ("7", "numero", "Siete"),
    ("8", "numero", "Ocho"),
    ("9", "numero", "Nueve"),
    ("×", "operador", "Multiplicación"),
    ("√", "operador", "Raíz cuadrada"),
    ("x²", "operador", "Cuadrado"),
    ("4", "numero", "Cuatro"),
    ("5", "numero", "Cinco"),
    ("6", "numero", "Seis"),
    ("−", "operador", "Resta"),
    ("ln", "operador", "Logaritmo natural"),
    ("log", "operador", "Logaritmo base 10"),
    ("1", "numero", "Uno"),
    ("2", "numero", "Dos"),
    ("3", "numero", "Tres"),
    ("+", "operador", "Suma"),
    ("π", "operador", "Constante pi"),
    ("e", "operador", "Constante e"),
    ("0", "numero", "Cero"),
    (".", "numero", "Punto decimal"),
    ("±", "operador", "Cambia signo"),
    ("mod", "operador", "Módulo (resto)"),
    ("|x|", "operador", "Valor absoluto"),
    ("1/x", "operador", "Inverso"),
    ("n!", "operador", "Factorial"),
    ("asin", "operador", "Arcoseno"),
    ("acos", "operador", "Arcocoseno"),
    ("atan", "operador", "Arcotangente"),
    ("=", "operador", "Calcula el resultado"),
]


class ErrorCalculo(Exception):
    pass


NOMBRES = {
    "pi": math.pi,
    "π": math.pi,
    "e": math.e,
    "tau": math.tau,
    "ans": 0.0,
}

FUNCIONES = (
    "sin",
    "cos",
    "tan",
    "asin",
    "acos",
    "atan",
    "ln",
    "log",
    "exp",
    "sqrt",
    "sqr",
    "abs",
    "round",
    "floor",
    "ceil",
    "sgn",
    "fact",
)


def formatear(valor, decimales=6):
    if valor != valor or valor in (float("inf"), float("-inf")):
        return "Error"
    if abs(valor) < 1e15 and abs(valor - round(valor)) < 1e-9:
        return str(int(round(valor)))
    texto = "{0:.{1}f}".format(valor, max(0, int(decimales)))
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto or "0"


def bonito(texto):
    reemplazos = [
        ("sqrt", "√"),
        ("sqr", "x²"),
        ("asin", "sen⁻¹"),
        ("acos", "cos⁻¹"),
        ("atan", "tan⁻¹"),
        ("pi", "π"),
        ("*", "×"),
        ("/", "÷"),
        ("-", "−"),
    ]
    for antes, despues in reemplazos:
        texto = texto.replace(antes, despues)
    return texto


class Motor:
    def __init__(self, angulo="deg"):
        self.angulo = angulo
        self.ultimo = 0.0

    def a_radianes(self, valor):
        if self.angulo == "deg":
            return math.radians(valor)
        if self.angulo == "grad":
            return math.radians(valor * 0.9)
        return valor

    def desde_radianes(self, valor):
        if self.angulo == "deg":
            return math.degrees(valor)
        if self.angulo == "grad":
            return math.degrees(valor) / 0.9
        return valor

    def evaluar(self, texto):
        self.tokens = self.tokenizar(texto)
        self.pos = 0
        if not self.tokens:
            raise ErrorCalculo("La expresion esta vacia")
        valor = self.expresion()
        if self.pos < len(self.tokens):
            raise ErrorCalculo("Sobro el dato: {0}".format(self.tokens[self.pos]))
        self.ultimo = valor
        return valor

    def tokenizar(self, texto):
        tokens = []
        indice = 0
        while indice < len(texto):
            caracter = texto[indice]
            if caracter.isspace():
                indice += 1
                continue
            if caracter.isdigit() or (
                caracter == "." and indice + 1 < len(texto) and texto[indice + 1].isdigit()
            ):
                fin = indice
                while fin < len(texto) and (texto[fin].isdigit() or texto[fin] == "."):
                    fin += 1
                if (
                    fin < len(texto)
                    and texto[fin] in "eE"
                    and fin + 1 < len(texto)
                    and (texto[fin + 1].isdigit() or texto[fin + 1] in "+-")
                ):
                    fin += 1
                    if texto[fin] in "+-":
                        fin += 1
                    while fin < len(texto) and texto[fin].isdigit():
                        fin += 1
                try:
                    tokens.append(float(texto[indice:fin]))
                except ValueError:
                    raise ErrorCalculo("Numero invalido: {0}".format(texto[indice:fin]))
                indice = fin
                continue
            if caracter.isalpha() or caracter in "π":
                fin = indice
                while fin < len(texto) and (texto[fin].isalnum() or texto[fin] in "π_"):
                    fin += 1
                nombre = texto[indice:fin].lower()
                if nombre == "mod":
                    tokens.append("%")
                else:
                    tokens.append(nombre)
                indice = fin
                continue
            if caracter == "√":
                tokens.append("sqrt")
                indice += 1
                continue
            if caracter in "+-*/^%(),!|":
                tokens.append(caracter)
                indice += 1
                continue
            raise ErrorCalculo("Caracter no valido: {0}".format(caracter))
        return tokens

    def actual(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def comer(self):
        token = self.actual()
        self.pos += 1
        return token

    def expresion(self):
        valor = self.termino()
        while self.actual() in ("+", "-"):
            operador = self.comer()
            otro = self.termino()
            valor = valor + otro if operador == "+" else valor - otro
        return valor

    def termino(self):
        valor = self.factor()
        while True:
            token = self.actual()
            if token in ("*", "/", "%"):
                self.comer()
                otro = self.factor()
                if token == "*":
                    valor = valor * otro
                elif token == "/":
                    if abs(otro) < 1e-12:
                        raise ErrorCalculo("No se puede dividir entre cero")
                    valor = valor / otro
                else:
                    if abs(otro) < 1e-12:
                        raise ErrorCalculo("No se puede sacar modulo de cero")
                    valor = valor % otro
            elif token == "(" or token in NOMBRES or token in FUNCIONES:
                valor = valor * self.factor()
            else:
                break
        return valor

    def factor(self):
        token = self.actual()
        if token in ("+", "-"):
            self.comer()
            valor = self.factor()
            return -valor if token == "-" else valor

        base = self.primario()
        if self.actual() == "^":
            self.comer()
            exponente = self.factor()
            try:
                return float(base) ** float(exponente)
            except OverflowError:
                raise ErrorCalculo("La potencia es muy grande")
            except (ValueError, ZeroDivisionError):
                raise ErrorCalculo("Potencia no valida")
        return base

    def primario(self):
        valor = self.atomo()
        while self.actual() == "!":
            self.comer()
            valor = self.factorial(valor)
        return valor

    def atomo(self):
        token = self.actual()
        if token is None:
            raise ErrorCalculo("Expresion incompleta")
        if isinstance(token, float):
            self.comer()
            return token
        if token == "(":
            self.comer()
            valor = self.expresion()
            if self.actual() != ")":
                raise ErrorCalculo("Falta cerrar el parentesis")
            self.comer()
            return valor
        if token in NOMBRES:
            self.comer()
            if token == "ans":
                return self.ultimo
            return NOMBRES[token]
        if token in FUNCIONES:
            self.comer()
            if self.actual() == "(":
                self.comer()
                valor = self.expresion()
                if self.actual() != ")":
                    raise ErrorCalculo("Falta cerrar el parentesis")
                self.comer()
            else:
                valor = self.factor()
            return self.aplicar(token, valor)
        raise ErrorCalculo("Dato no valido: {0}".format(token))

    def aplicar(self, nombre, valor):
        try:
            if nombre == "sin":
                return math.sin(self.a_radianes(valor))
            if nombre == "cos":
                return math.cos(self.a_radianes(valor))
            if nombre == "tan":
                return math.tan(self.a_radianes(valor))
            if nombre == "asin":
                if not -1.0 <= valor <= 1.0:
                    raise ErrorCalculo("El dominio de sen⁻¹ es -1 a 1")
                return self.desde_radianes(math.asin(valor))
            if nombre == "acos":
                if not -1.0 <= valor <= 1.0:
                    raise ErrorCalculo("El dominio de cos⁻¹ es -1 a 1")
                return self.desde_radianes(math.acos(valor))
            if nombre == "atan":
                return self.desde_radianes(math.atan(valor))
            if nombre == "ln":
                if valor <= 0:
                    raise ErrorCalculo("El logaritmo necesita un numero positivo")
                return math.log(valor)
            if nombre == "log":
                if valor <= 0:
                    raise ErrorCalculo("El logaritmo necesita un numero positivo")
                return math.log10(valor)
            if nombre == "exp":
                return math.exp(valor)
            if nombre == "sqrt":
                if valor < 0:
                    raise ErrorCalculo("La raiz necesita un numero positivo")
                return math.sqrt(valor)
            if nombre == "sqr":
                return valor * valor
            if nombre == "abs":
                return abs(valor)
            if nombre == "round":
                return float(round(valor))
            if nombre == "floor":
                return float(math.floor(valor))
            if nombre == "ceil":
                return float(math.ceil(valor))
            if nombre == "sgn":
                return float((valor > 0) - (valor < 0))
            if nombre == "fact":
                return self.factorial(valor)
        except OverflowError:
            raise ErrorCalculo("El resultado es muy grande")
        except ValueError:
            raise ErrorCalculo("No se puede calcular {0}".format(nombre))
        raise ErrorCalculo("Funcion desconocida: {0}".format(nombre))

    def factorial(self, valor):
        if valor < 0 or valor != int(valor) or valor > 170:
            raise ErrorCalculo("El factorial va de 0 a 170 enteros")
        return float(math.factorial(int(valor)))


class HistorialDialog(QDialog):
    def __init__(self, parent=None, historial=None):
        super().__init__(parent)
        self.historial = historial or []
        self.setWindowTitle("Historial de calculos")
        self.setModal(True)
        self.resize(540, 440)
        self.setStyleSheet(TEMA)

        encabezado = QLabel("CALCULOS REALIZADOS")
        encabezado.setFont(QFont("Segoe UI", 12, QFont.Bold))
        encabezado.setAlignment(Qt.AlignCenter)

        self.txt_historial = QTextEdit()
        self.txt_historial.setReadOnly(True)
        self.txt_historial.setFont(QFont("Consolas", 11))

        self.ck_mayusculas = QCheckBox("Mostrar en mayusculas")
        self.ck_mayusculas.stateChanged.connect(lambda _e: self.pintar())

        self.cmb_tamanio = QComboBox()
        self.cmb_tamanio.addItems(["Pequeno", "Normal", "Grande"])
        self.cmb_tamanio.setCurrentIndex(1)
        self.cmb_tamanio.currentIndexChanged.connect(self.cambiar_tamanio)

        opciones = QHBoxLayout()
        opciones.addWidget(self.ck_mayusculas)
        opciones.addWidget(QLabel("Fuente:"))
        opciones.addWidget(self.cmb_tamanio)
        opciones.addStretch()

        self.rb_cientifico = QRadioButton("Notacion cientifica")
        self.rb_normal = QRadioButton("Notacion normal")
        self.rb_normal.setChecked(True)
        self.rb_normal.toggled.connect(lambda _v: self.pintar())

        forma = QHBoxLayout()
        forma.addWidget(self.rb_cientifico)
        forma.addWidget(self.rb_normal)
        forma.addStretch()

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(self.reject)
        botones.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(encabezado)
        layout.addWidget(self.txt_historial)
        layout.addLayout(opciones)
        layout.addLayout(forma)
        layout.addWidget(botones)

        self.pintar()

    def cambiar_tamanio(self, indice):
        self.txt_historial.setFont(QFont("Consolas", [10, 11, 14][indice]))

    def pintar(self):
        if not self.historial:
            self.txt_historial.setPlainText("Todavia no hay calculos guardados.")
            return

        cientifico = self.rb_cientifico.isChecked()
        mayusculas = self.ck_mayusculas.isChecked()

        lineas = []
        for indice, item in enumerate(self.historial, start=1):
            valor = item["resultado"]
            if cientifico:
                try:
                    valor = "{0:.6e}".format(float(valor))
                except ValueError:
                    pass
            linea = "{0:02d}. {1} = {2}   [{3}]".format(
                indice, bonito(item["expresion"]), valor, item.get("fecha", "")
            )
            lineas.append(linea.upper() if mayusculas else linea)

        self.txt_historial.setPlainText("\n".join(lineas))


class AcercaDeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acerca de {}".format(TITULO))
        self.setModal(True)
        self.setMinimumWidth(430)
        self.setStyleSheet(TEMA)

        titulo = QLabel(TITULO)
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)

        self.txt_acerca = QTextEdit()
        self.txt_acerca.setReadOnly(True)
        self.txt_acerca.setPlainText(
            "Calculadora cientifica con memoria, historial y\nevaluador de expresiones propio (sin eval).\n\n"
            "PyQt5: QApplication, QMainWindow, QWidget, QDialog,\n"
            "QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,\n"
            "QCheckBox, QRadioButton, QAction, QActionGroup,\n"
            "QMenuBar, QMenu, QGroupBox, QGridLayout,\n"
            "QVBoxLayout, QHBoxLayout, QFormLayout, QFrame,\n"
            "QDialogButtonBox, QMessageBox, QTimer, señales/slots\n"
            "y eventos de teclado, ratón y rueda.\n\n"
            "PyQt5 sobre Python 3\n\n"
            "Fue echo por el echicero"
        )

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(self.reject)
        botones.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(titulo)
        layout.addWidget(self.txt_acerca)
        layout.addWidget(botones)


class AjustesDialog(QDialog):
    Guardado = pyqtSignal(str, int, bool, bool)

    def __init__(self, parent=None, angulo="deg", decimales=6, historial=True, panel=True):
        super().__init__(parent)
        self.setWindowTitle("Ajustes de la calculadora")
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet(TEMA)

        self.cmb_angulo = QComboBox()
        for clave, texto in MODOS:
            self.cmb_angulo.addItem(texto, clave)
        indice = [clave for clave, _ in MODOS].index(angulo)
        self.cmb_angulo.setCurrentIndex(indice)

        self.cmb_decimales = QComboBox()
        self.cmb_decimales.addItems([str(n) for n in range(0, 11)])
        self.cmb_decimales.setCurrentText(str(decimales))

        self.ck_historial = QCheckBox("Guardar los calculos en el historial")
        self.ck_historial.setChecked(historial)
        self.ck_panel = QCheckBox("Mostrar el historial en la ventana principal")
        self.ck_panel.setChecked(panel)

        formulario = QFormLayout()
        formulario.addRow("Modo angular:", self.cmb_angulo)
        formulario.addRow("Decimales:", self.cmb_decimales)
        formulario.addRow("Opciones:", self.ck_historial)
        formulario.addRow(" ", self.ck_panel)

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("GUARDAR")
        botones.button(QDialogButtonBox.Cancel).setText("CANCELAR")
        botones.accepted.connect(self.aceptar)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(formulario)
        layout.addWidget(botones)

    def aceptar(self):
        self.Guardado.emit(
            self.cmb_angulo.currentData(),
            int(self.cmb_decimales.currentText()),
            self.ck_historial.isChecked(),
            self.ck_panel.isChecked(),
        )
        self.accept()


class VentanaPrincipal(QMainWindow):
    notificado = pyqtSignal(str)
    calculado = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(TITULO)
        self.setStyleSheet(TEMA)
        self.resize(1080, 720)

        self.modo = "deg"
        self.decimales = 6
        self.motor = Motor(self.modo)
        self.memoria = 0.0
        self.historial = []
        self.guardar_historial = True
        self.mostrar_panel = True
        self.cargar_datos()

        self.crear_ui()
        self.crear_menus()
        self.mostrar_memoria()

        self.notificado.connect(self.mostrar_notificacion)
        self.calculado.connect(self.al_terminar_calculo)

        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.tick_reloj)
        self.timer_reloj.start(1000)

        self.timer_guardado = QTimer(self)
        self.timer_guardado.timeout.connect(self.guardado_automatico)
        self.timer_guardado.start(30000)

        self.notificado.emit(
            "{} lista. F1 ayuda :: F2 ajustes :: Enter calcula".format(TITULO)
        )

    # ---------------------------------------------------------------- interfaz

    def crear_ui(self):
        contenedor = QWidget()
        self.setCentralWidget(contenedor)

        raiz = QVBoxLayout(contenedor)

        cabecera = QHBoxLayout()
        self.lbl_titulo = QLabel(TITULO)
        self.lbl_titulo.setFont(QFont("Segoe UI", 18, QFont.Bold))

        self.lbl_reloj = QLabel("--:--:--")
        self.lbl_reloj.setFont(QFont("Consolas", 13))
        self.lbl_reloj.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        cabecera.addWidget(self.lbl_titulo, 1)
        cabecera.addWidget(self.lbl_reloj)
        raiz.addLayout(cabecera)

        self.lbl_subtitulo = QLabel("Menuus :: F1 ayuda :: F2 ajustes :: doble clic limpia")
        self.lbl_subtitulo.setObjectName("rotulo")
        self.lbl_subtitulo.setAlignment(Qt.AlignCenter)
        raiz.addWidget(self.lbl_subtitulo)

        panel = QWidget()
        raiz.addWidget(panel, 1)
        fila_panel = QHBoxLayout(panel)
        self.crear_panel_teclado(fila_panel)
        self.crear_panel_lateral(fila_panel)

        raiz.addWidget(self.crear_barra_estado())

        pie = QLabel("Fue echo por el echicero")
        pie.setObjectName("rotulo")
        pie.setAlignment(Qt.AlignCenter)
        raiz.addWidget(pie)

        self.lbl_estado = QLabel("Esperando datos...")
        self.lbl_estado.setObjectName("rotulo")
        self.lbl_estado.setWordWrap(True)
        self.lbl_estado.setAlignment(Qt.AlignCenter)
        raiz.addWidget(self.lbl_estado)

    def crear_panel_teclado(self, layout_padre):
        grupo = QGroupBox("TECLADO")
        layout = QVBoxLayout(grupo)

        marco_pantalla = QFrame()
        marco_pantalla.setObjectName("marco_pantalla")
        dentro = QVBoxLayout(marco_pantalla)
        dentro.setContentsMargins(10, 8, 10, 8)

        self.lbl_memoria = QLabel("M: 0")
        self.lbl_memoria.setObjectName("memoria")
        self.lbl_memoria.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.txt_expresion = QLineEdit()
        self.txt_expresion.setObjectName("pantalla")
        self.txt_expresion.setReadOnly(True)
        self.txt_expresion.setAlignment(Qt.AlignRight)
        self.txt_expresion.setMinimumHeight(42)

        self.lbl_resultado = QLabel("= 0")
        self.lbl_resultado.setObjectName("resultado")
        self.lbl_resultado.setFont(QFont("Consolas", 24, QFont.Bold))
        self.lbl_resultado.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_resultado.setMinimumHeight(48)

        dentro.addWidget(self.lbl_memoria)
        dentro.addWidget(self.txt_expresion)
        dentro.addWidget(self.lbl_resultado)
        layout.addWidget(marco_pantalla)

        self.txt_expresion.textChanged.connect(self.al_texto_cambiado)

        cuadricula = QGridLayout()
        cuadricula.setVerticalSpacing(6)
        cuadricula.setHorizontalSpacing(6)
        self.botones = {}

        for posicion, (etiqueta, clase, ayuda) in enumerate(TECLAS):
            boton = QPushButton(etiqueta)
            boton.setObjectName("igual" if etiqueta == "=" else clase)
            boton.setToolTip(ayuda)
            boton.setStatusTip(ayuda)
            boton.setMinimumHeight(40)
            boton.setMinimumWidth(58)
            if clase == "numero":
                boton.setFont(QFont("Segoe UI", 15, QFont.Bold))
            boton.clicked.connect(lambda _c=False, t=etiqueta: self.pulsar(t))
            self.botones[etiqueta] = boton

            if etiqueta == "=":
                cuadricula.addWidget(boton, 6, 4, 1, 2)
            else:
                cuadricula.addWidget(boton, posicion // 6, posicion % 6)

        layout.addLayout(cuadricula, 1)
        layout_padre.addWidget(grupo, 3)

    def crear_panel_lateral(self, layout_padre):
        grupo = QGroupBox("MEMORIA E HISTORIAL")
        layout = QVBoxLayout(grupo)

        self.cmb_angulo = QComboBox()
        for clave, texto in MODOS:
            self.cmb_angulo.addItem(texto, clave)
        self.cmb_angulo.setCurrentIndex([clave for clave, _ in MODOS].index(self.modo))
        self.cmb_angulo.currentIndexChanged.connect(self.al_cambiar_modo)

        self.ck_memoria = QCheckBox("Ver panel")
        self.ck_memoria.setChecked(True)
        self.ck_memoria.stateChanged.connect(self.al_cambiar_panel)

        self.ck_guardar = QCheckBox("Guardar historial")
        self.ck_guardar.setChecked(self.guardar_historial)
        self.ck_guardar.stateChanged.connect(self.al_cambiar_guardado)

        formulario = QFormLayout()
        formulario.addRow("Modo angular:", self.cmb_angulo)
        formulario.addRow("Panel:", self.ck_memoria)
        formulario.addRow("Historial:", self.ck_guardar)

        layout.addLayout(formulario)

        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        layout.addWidget(separador)

        self.lbl_contador = QLabel("Calculos: 0")
        self.lbl_contador.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(self.lbl_contador)

        self.txt_historial = QTextEdit()
        self.txt_historial.setReadOnly(True)
        self.txt_historial.setFont(QFont("Consolas", 10))
        layout.addWidget(self.txt_historial, 1)

        self.lbl_resumen = QLabel("Memoria: 0")
        self.lbl_resumen.setObjectName("rotulo")
        self.lbl_resumen.setWordWrap(True)
        layout.addWidget(self.lbl_resumen)

        self.lbl_mensaje = QLabel("Listo para calcular")
        self.lbl_mensaje.setObjectName("rotulo")
        self.lbl_mensaje.setWordWrap(True)
        self.lbl_mensaje.setVisible(self.mostrar_panel)
        layout.addWidget(self.lbl_mensaje)

        self.btn_historial = QPushButton("HISTORIAL")
        self.btn_limpiar_historial = QPushButton("LIMPIAR")
        self.btn_ajustes = QPushButton("AJUSTES")
        self.btn_copiar = QPushButton("COPIAR")
        self.btn_exportar = QPushButton("EXPORTAR")

        self.btn_historial.clicked.connect(self.ver_historial)
        self.btn_limpiar_historial.clicked.connect(self.limpiar_historial)
        self.btn_ajustes.clicked.connect(self.abrir_ajustes)
        self.btn_copiar.clicked.connect(self.copiar_resultado)
        self.btn_exportar.clicked.connect(self.exportar)

        primera = QHBoxLayout()
        primera.addWidget(self.btn_historial)
        primera.addWidget(self.btn_ajustes)
        layout.addLayout(primera)

        segunda = QHBoxLayout()
        segunda.addWidget(self.btn_copiar)
        segunda.addWidget(self.btn_exportar)
        segunda.addWidget(self.btn_limpiar_historial)
        layout.addLayout(segunda)

        layout_padre.addWidget(grupo, 2)

    def crear_barra_estado(self):
        marco = QFrame()
        marco.setFrameShape(QFrame.StyledPanel)
        layout = QHBoxLayout(marco)

        self.lbl_modo = QLabel("MODO: GRADOS")
        self.lbl_modo.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.lbl_operacion = QLabel("Listo")
        self.lbl_operacion.setAlignment(Qt.AlignCenter)

        self.lbl_ultimo = QLabel("Ultimo: -")
        self.lbl_ultimo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(self.lbl_modo)
        layout.addWidget(self.lbl_operacion, 1)
        layout.addWidget(self.lbl_ultimo)
        return marco

    def crear_menus(self):
        barra = self.menuBar()
        self.acciones = {}

        archivo = barra.addMenu("&Archivo")
        accion_nuevo = QAction("&Nuevo calculo", self)
        accion_nuevo.setShortcut(QKeySequence.New)
        accion_nuevo.setStatusTip("Limpia la entrada para empezar de cero")
        accion_nuevo.triggered.connect(self.limpiar_todo)
        archivo.addAction(accion_nuevo)

        accion_guardar = QAction("&Guardar", self)
        accion_guardar.setShortcut(QKeySequence.Save)
        accion_guardar.setStatusTip("Guarda memoria, historial y ajustes en el disco")
        accion_guardar.triggered.connect(self.guardar_datos)
        archivo.addAction(accion_guardar)

        accion_exportar = QAction("&Exportar reporte...", self)
        accion_exportar.setShortcut("Ctrl+E")
        accion_exportar.setStatusTip("Exporta el historial a un archivo de texto")
        accion_exportar.triggered.connect(self.exportar)
        archivo.addAction(accion_exportar)

        archivo.addSeparator()

        accion_salir = QAction("&Salir", self)
        accion_salir.setShortcut("Ctrl+Q")
        accion_salir.setStatusTip("Cierra la calculadora")
        accion_salir.triggered.connect(self.close)
        archivo.addAction(accion_salir)

        edicion = barra.addMenu("&Editar")
        accion_copiar = QAction("&Copiar resultado", self)
        accion_copiar.setShortcut(QKeySequence.Copy)
        accion_copiar.setStatusTip("Copia el resultado al portapapeles")
        accion_copiar.triggered.connect(self.copiar_resultado)
        edicion.addAction(accion_copiar)

        accion_pegar = QAction("&Pegar numero", self)
        accion_pegar.setShortcut(QKeySequence.Paste)
        accion_pegar.setStatusTip("Pega un numero desde el portapapeles")
        accion_pegar.triggered.connect(self.pegar_numero)
        edicion.addAction(accion_pegar)

        accion_borrar = QAction("&Borrar historial", self)
        accion_borrar.setShortcut("Ctrl+Shift+B")
        accion_borrar.setStatusTip("Borra todos los calculos guardados")
        accion_borrar.triggered.connect(self.limpiar_historial)
        edicion.addAction(accion_borrar)

        edicion.addSeparator()

        accion_ajustes = QAction("&Ajustes...", self)
        accion_ajustes.setShortcut("F2")
        accion_ajustes.setStatusTip("Modo angular, decimales y paneles")
        accion_ajustes.triggered.connect(self.abrir_ajustes)
        edicion.addAction(accion_ajustes)

        ver = barra.addMenu("&Ver")
        menu_modo = ver.addMenu("Modo angular")
        grupo_modo = QActionGroup(self)
        grupo_modo.setExclusive(True)
        for indice, (clave, texto) in enumerate(MODOS):
            accion = QAction(texto, self, checkable=True)
            accion.setData(clave)
            accion.setShortcut("Ctrl+{0}".format(indice + 1))
            accion.setStatusTip("Trabaja las trigonometricas en {0}".format(texto.lower()))
            accion.setChecked(clave == self.modo)
            accion.triggered.connect(self.al_elegir_modo)
            grupo_modo.addAction(accion)
            menu_modo.addAction(accion)
            self.acciones["modo_{0}".format(indice)] = accion

        ver.addSeparator()

        accion_panel = QAction("Mostrar &panel de memoria", self, checkable=True)
        accion_panel.setChecked(self.mostrar_panel)
        accion_panel.setShortcut("Ctrl+M")
        accion_panel.setStatusTip("Muestra u oculta el panel lateral")
        accion_panel.triggered.connect(self.alternar_panel)
        ver.addAction(accion_panel)

        calculadora = barra.addMenu("&Calculadora")
        menu_rapidas = calculadora.addMenu("Operaciones rapidas")
        for etiqueta, expresion, atajo in [
            ("Cuadrado del ultimo", "ans^2", "Ctrl+U"),
            ("Raiz del ultimo", "√(ans)", "Ctrl+R"),
            ("Inverso del ultimo", "1/ans", "Ctrl+I"),
            ("Porcentaje del ultimo", "(ans/100)", "Ctrl+P"),
        ]:
            accion = QAction(etiqueta, self)
            accion.setShortcut(atajo)
            accion.setStatusTip("Escribe {0} en la entrada".format(expresion))
            accion.triggered.connect(lambda _m=False, e=expresion: self.escribir(e))
            menu_rapidas.addAction(accion)

        menu_memoria = calculadora.addMenu("Memoria")
        for etiqueta, comando, atajo in [
            ("Limpiar memoria (MC)", "MC", "Ctrl+Shift+M"),
            ("Traer memoria (MR)", "MR", "Ctrl+Alt+M"),
            ("Sumar a la memoria (M+)", "M+", "Ctrl+Alt+A"),
            ("Restar de la memoria (M-)", "M-", "Ctrl+Alt+R"),
        ]:
            accion = QAction(etiqueta, self)
            accion.setShortcut(atajo)
            accion.setStatusTip(etiqueta)
            accion.triggered.connect(
                lambda _marcado=False, c=comando: self.operar_memoria(c)
            )
            menu_memoria.addAction(accion)

        calculadora.addSeparator()

        accion_igual = QAction("Calcular (&=)", self)
        accion_igual.setShortcut("Return")
        accion_igual.setStatusTip("Evalua la expresion de la entrada")
        accion_igual.triggered.connect(self.calcular)
        calculadora.addAction(accion_igual)

        ayuda = barra.addMenu("A&yuda")
        accion_atajos = QAction("&Atajos de teclado...", self)
        accion_atajos.setShortcut("F1")
        accion_atajos.setStatusTip("Muestra la lista de atajos")
        accion_atajos.triggered.connect(self.mostrar_atajos)
        ayuda.addAction(accion_atajos)

        accion_funciones = QAction("&Funciones disponibles...", self)
        accion_funciones.setStatusTip("Lista de funciones del motor de calculo")
        accion_funciones.triggered.connect(self.mostrar_funciones)
        ayuda.addAction(accion_funciones)

        accion_acerca = QAction("&Acerca de...", self)
        accion_acerca.setStatusTip("Informacion del sistema")
        accion_acerca.triggered.connect(self.mostrar_acerca_de)
        ayuda.addAction(accion_acerca)

        for accion in self.findChildren(QAction):
            accion.hovered.connect(self.al_hover_accion)

    def al_hover_accion(self, _marcado=False):
        accion = self.sender()
        if accion is None:
            return
        self.statusBar().showMessage(accion.statusTip() or accion.text())

    def al_elegir_modo(self):
        accion = self.sender()
        self.cambiar_modo(accion.data())
        self.notificado.emit("Modo angular: {0}".format(self.texto_modo()))

    def texto_modo(self):
        for clave, texto in MODOS:
            if clave == self.modo:
                return texto
        return "Grados"

    def cambiar_modo(self, modo):
        if modo not in [clave for clave, _ in MODOS]:
            modo = "deg"
        self.modo = modo
        self.motor.angulo = modo
        indice = [clave for clave, _ in MODOS].index(modo)
        self.cmb_angulo.blockSignals(True)
        self.cmb_angulo.setCurrentIndex(indice)
        self.cmb_angulo.blockSignals(False)
        for posicion, (clave, _texto) in enumerate(MODOS):
            self.acciones["modo_{0}".format(posicion)].setChecked(clave == modo)
        self.lbl_modo.setText("MODO: {0}".format(self.texto_modo().upper()))

    def formatear(self, valor):
        return formatear(valor, self.decimales)

    def pulsar(self, etiqueta):
        if etiqueta in ("C", "CE"):
            if etiqueta == "C":
                self.limpiar_todo()
            else:
                self.limpiar_entrada()
            return
        if etiqueta == "⌫":
            self.borrar_ultimo()
            return
        if etiqueta == "=":
            self.calcular()
            return
        if etiqueta in ("MC", "MR", "M+", "M-"):
            self.operar_memoria(etiqueta)
            return

        if etiqueta == "x²":
            self.escribir("^2")
        elif etiqueta == "x^y":
            self.escribir("^")
        elif etiqueta == "1/x":
            self.escribir("1/(")
        elif etiqueta == "n!":
            self.escribir("!")
        elif etiqueta == "|x|":
            self.escribir("abs(")
        elif etiqueta == "mod":
            self.escribir("%")
        elif etiqueta == "%":
            self.escribir("/100")
        elif etiqueta == "±":
            self.cambiar_signo()
        elif etiqueta == "√":
            self.escribir("√(")
        elif etiqueta == "π":
            self.escribir("pi")
        elif etiqueta in ("asin", "acos", "atan", "sin", "cos", "tan", "ln", "log", "exp"):
            self.escribir(etiqueta + "(")
        elif etiqueta == "e":
            self.escribir("e")
        else:
            self.escribir(etiqueta)

    def escribir(self, texto):
        actual = self.txt_expresion.text()
        valor = texto.startswith(
            ("sin(", "cos(", "tan(", "ln(", "log(", "exp(", "√(", "abs(", "pi", "e", "(", "1/(", "ans")
        )
        if actual and valor and (
            actual[-1:].isdigit() or actual[-1:] in ".)" or actual.endswith("!")
        ):
            actual += "*"
        for simbolo, ascii_ in (("×", "*"), ("÷", "/"), ("−", "-")):
            texto = texto.replace(simbolo, ascii_)
        self.txt_expresion.setText(actual + texto)
        self.txt_expresion.setCursorPosition(len(self.txt_expresion.text()))

    def cerrar_parentesis(self, texto):
        faltan = texto.count("(") - texto.count(")")
        if faltan > 0:
            texto += ")" * faltan
        return texto

    def borrar_ultimo(self):
        texto = self.txt_expresion.text()
        self.txt_expresion.setText(texto[:-1])

    def cambiar_signo(self):
        texto = self.txt_expresion.text()
        if texto.startswith("-"):
            self.txt_expresion.setText(texto[1:])
        else:
            self.txt_expresion.setText("-" + texto)

    def limpiar_entrada(self):
        self.txt_expresion.clear()
        self.lbl_resultado.setText("= 0")
        self.lbl_operacion.setText("Entrada limpia")
        self.txt_expresion.setFocus()

    def limpiar_todo(self):
        self.limpiar_entrada()
        self.motor.ultimo = 0.0
        self.lbl_ultimo.setText("Ultimo: -")
        self.notificado.emit("Calculadora reiniciada")

    def al_texto_cambiado(self, texto):
        self.lbl_operacion.setText("Expresion: {0}".format(bonito(texto) or "vacia"))

    def calcular(self):
        texto = self.cerrar_parentesis(self.txt_expresion.text().strip())
        if not texto:
            self.notificado.emit("Escribe algo antes de calcular")
            return

        try:
            valor = self.motor.evaluar(texto)
        except ErrorCalculo as error:
            self.lbl_operacion.setText("Error: {0}".format(error))
            self.notificado.emit("Error: {0}".format(error))
            QMessageBox.warning(self, "No se pudo calcular", str(error))
            return
        except Exception:
            self.lbl_operacion.setText("Error: expresion no valida")
            self.notificado.emit("Error: expresion no valida")
            QMessageBox.warning(self, "No se pudo calcular", "La expresion no es valida.")
            return

        if valor != valor or valor in (float("inf"), float("-inf")):
            self.lbl_operacion.setText("Error: resultado indefinido")
            self.notificado.emit("Error: resultado indefinido")
            QMessageBox.warning(self, "No se pudo calcular", "El resultado no existe.")
            return

        resultado = self.formatear(valor)
        self.lbl_resultado.setText("= {0}".format(resultado))
        self.lbl_ultimo.setText("Ultimo: {0}".format(resultado))
        self.txt_expresion.setText(resultado)
        self.calculado.emit(texto, resultado)

        if self.guardar_historial:
            self.historial.insert(
                0,
                {
                    "expresion": texto,
                    "resultado": resultado,
                    "fecha": datetime.now().strftime("%H:%M:%S"),
                    "modo": self.modo,
                },
            )
            del self.historial[200:]
            self.mostrar_historial()

        self.guardar_datos()

    def al_terminar_calculo(self, expresion, resultado):
        self.statusBar().showMessage(
            "{0} = {1}".format(bonito(expresion), resultado), 4000
        )

    def mostrar_notificacion(self, mensaje):
        self.lbl_estado.setText(mensaje)
        if hasattr(self, "lbl_mensaje"):
            self.lbl_mensaje.setText(mensaje)

    def operar_memoria(self, etiqueta):
        actual = self.motor.ultimo

        if etiqueta == "MC":
            self.memoria = 0.0
            self.notificado.emit("Memoria borrada")
        elif etiqueta == "MR":
            self.escribir(self.formatear(self.memoria))
            self.notificado.emit("Memoria: {0}".format(self.formatear(self.memoria)))
            return
        elif etiqueta == "M+":
            self.memoria += actual
            self.notificado.emit("Memoria: {0}".format(self.formatear(self.memoria)))
        elif etiqueta == "M-":
            self.memoria -= actual
            self.notificado.emit("Memoria: {0}".format(self.formatear(self.memoria)))

        self.mostrar_memoria()
        self.guardar_datos()

    def mostrar_memoria(self):
        self.lbl_memoria.setText("M: {0}".format(self.formatear(self.memoria)))
        self.lbl_resumen.setText(
            "Memoria: {0} | Calculos: {1}".format(
                self.formatear(self.memoria), len(self.historial)
            )
        )

    def mostrar_historial(self):
        if not self.historial:
            self.txt_historial.setPlainText("Todavia no hay calculos.")
        else:
            lineas = [
                "{0:02d}. {1} = {2}".format(
                    indice, bonito(item["expresion"]), item["resultado"]
                )
                for indice, item in enumerate(self.historial[:60], start=1)
            ]
            self.txt_historial.setPlainText("\n".join(lineas))
        self.lbl_contador.setText("Calculos: {0}".format(len(self.historial)))
        self.mostrar_memoria()

    def ver_historial(self):
        dialogo = HistorialDialog(self, self.historial)
        dialogo.exec_()

    def limpiar_historial(self):
        if not self.historial:
            QMessageBox.information(self, "Aviso", "El historial ya esta vacio.")
            return

        respuesta = QMessageBox.question(self, "Borrar historial", "Borrar todos los calculos?")
        if respuesta == QMessageBox.Yes:
            self.historial = []
            self.mostrar_historial()
            self.guardar_datos()
            self.notificado.emit("Historial borrado")

    def abrir_ajustes(self):
        dialogo = AjustesDialog(
            self, self.modo, self.decimales, self.guardar_historial, self.mostrar_panel
        )
        dialogo.Guardado.connect(self.aplicar_ajustes)
        dialogo.exec_()

    def aplicar_ajustes(self, modo, decimales, guardar, panel):
        self.cambiar_modo(modo)
        self.decimales = decimales
        self.guardar_historial = guardar
        self.mostrar_panel = panel
        self.ck_guardar.setChecked(guardar)
        self.ck_memoria.setChecked(panel)
        self.lbl_mensaje.setVisible(panel)
        self.al_cambiar_panel(None)
        self.guardar_datos()
        self.notificado.emit("Ajustes guardados")

    def copiar_resultado(self):
        resultado = self.lbl_resultado.text().replace("=", "").strip()
        if not resultado:
            QMessageBox.information(self, "Aviso", "No hay ningun resultado que copiar.")
            return
        QApplication.clipboard().setText(resultado)
        self.notificado.emit("Copiado: {0}".format(resultado))

    def pegar_numero(self):
        texto = QApplication.clipboard().text().strip()
        limpio = "".join(caracter for caracter in texto if caracter.isdigit() or caracter in ".,-")
        if not limpio:
            QMessageBox.information(self, "Aviso", "El portapapeles no tiene numeros.")
            return
        self.escribir(limpio.replace(",", "."))
        self.notificado.emit("Pegado: {0}".format(limpio))

    def exportar(self):
        if not self.historial:
            QMessageBox.information(self, "Aviso", "No hay calculos para exportar.")
            return

        with open(ARCHIVO_REPORTE, "w", encoding="utf-8") as archivo:
            archivo.write("{} - REPORTE\n".format(TITULO))
            archivo.write("Fue echo por el echicero\n")
            archivo.write("=" * 60 + "\n")
            for posicion, item in enumerate(self.historial, start=1):
                archivo.write(
                    "{0}. {1} = {2} | modo: {3} | {4}\n".format(
                        posicion,
                        item["expresion"],
                        item["resultado"],
                        item.get("modo", "-"),
                        item.get("fecha", ""),
                    )
                )
            archivo.write("-" * 60 + "\n")
            archivo.write("Total de calculos: {0}\n".format(len(self.historial)))
            archivo.write("Memoria actual: {0}\n".format(formatear(self.memoria)))

        QMessageBox.information(
            self, "Exportar", "Reporte guardado en:\n{0}".format(ARCHIVO_REPORTE)
        )
        self.notificado.emit("Reporte exportado en {0}".format(ARCHIVO_REPORTE))

    def guardar_datos(self):
        datos = {
            "historial": self.historial,
            "memoria": self.memoria,
            "modo": self.modo,
            "decimales": self.decimales,
            "guardar_historial": self.guardar_historial,
            "mostrar_panel": self.mostrar_panel,
        }
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=2, ensure_ascii=False)

    def cargar_datos(self):
        if not os.path.exists(ARCHIVO_DATOS):
            return
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (json.JSONDecodeError, OSError):
            return

        self.historial = datos.get("historial", [])[:200]
        self.memoria = float(datos.get("memoria", 0.0) or 0.0)
        self.modo = datos.get("modo", "deg")
        self.guardar_historial = bool(datos.get("guardar_historial", True))
        self.mostrar_panel = bool(datos.get("mostrar_panel", True))
        try:
            self.decimales = int(datos.get("decimales", self.decimales))
        except (TypeError, ValueError):
            self.decimales = 6
        if self.modo not in [clave for clave, _ in MODOS]:
            self.modo = "deg"
        self.motor.angulo = self.modo

    def al_cambiar_modo(self, _indice):
        self.cambiar_modo(self.cmb_angulo.currentData())

    def al_cambiar_panel(self, _estado):
        self.mostrar_panel = self.ck_memoria.isChecked()
        self.lbl_mensaje.setVisible(self.mostrar_panel)
        self.txt_historial.setVisible(self.mostrar_panel)

    def al_cambiar_guardado(self, _estado):
        self.guardar_historial = self.ck_guardar.isChecked()
        self.notificado.emit(
            "Historial {0}".format("activado" if self.guardar_historial else "desactivado")
        )

    def alternar_panel(self):
        self.ck_memoria.setChecked(not self.ck_memoria.isChecked())

    def mostrar_atajos(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Atajos de teclado")
        dialogo.setModal(True)
        dialogo.setMinimumWidth(430)
        dialogo.setStyleSheet(TEMA)

        lista = QTextEdit()
        lista.setReadOnly(True)
        lista.setPlainText(
            "Enter       Calcular el resultado\n"
            "Esc         Borrar la entrada\n"
            "Retroceso   Borrar el ultimo caracter\n"
            "Ctrl+N      Nuevo calculo\n"
            "Ctrl+S      Guardar en el disco\n"
            "Ctrl+E      Exportar reporte\n"
            "Ctrl+C      Copiar el resultado\n"
            "Ctrl+V      Pegar un numero\n"
            "Ctrl+M      Mostrar u ocultar el panel\n"
            "Ctrl+1/2/3  Grados, radianes, gradianes\n"
            "Ctrl+R      Raiz del ultimo resultado\n"
            "Ctrl+U      Cuadrado del ultimo resultado\n"
            "Ctrl+I      Inverso del ultimo resultado\n"
            "Ctrl+Shift+B Borrar el historial\n"
            "F1          Esta ayuda\n"
            "F2          Ajustes\n"
            "Rueda       Ajusta el resultado (Ctrl cambia el signo)\n"
            "Doble clic  Limpia la entrada"
        )

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(dialogo.reject)
        botones.accepted.connect(dialogo.accept)

        layout = QVBoxLayout(dialogo)
        layout.addWidget(QLabel("Atajos disponibles"))
        layout.addWidget(lista)
        layout.addWidget(botones)
        dialogo.exec_()

    def mostrar_funciones(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Funciones del motor")
        dialogo.setModal(True)
        dialogo.setMinimumWidth(430)
        dialogo.setStyleSheet(TEMA)

        lista = QTextEdit()
        lista.setReadOnly(True)
        lista.setPlainText(
            " trigonometricas\n"
            "  sin(x) cos(x) tan(x) en el modo angular elegido\n"
            "  asin(x) acos(x) atan(x) devuelven el modo angular\n"
            "  logaritmos\n"
            "  ln(x) logaritmo natural\n"
            "  log(x) logaritmo base 10\n"
            "  potencias y raices\n"
            "  x^y potencia\n"
            "  x² con el boton x2, √(x) con el boton raiz\n"
            "  exp(x) e elevado a x\n"
            "  n! factorial de 0 a 170\n"
            "  otras\n"
            "  abs(x) valor absoluto\n"
            "  mod (%) resto de la division\n"
            "  pi y e constantes\n"
            "  ans ultimo resultado\n"
            "  parentesis () para agrupar\n"
            "  ejemplo: sin(30)+cos(60)*2"
        )

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(dialogo.reject)
        botones.accepted.connect(dialogo.accept)

        layout = QVBoxLayout(dialogo)
        layout.addWidget(QLabel("Funciones disponibles"))
        layout.addWidget(lista)
        layout.addWidget(botones)
        dialogo.exec_()

    def mostrar_acerca_de(self):
        dialogo = AcercaDeDialog(self)
        dialogo.exec_()

    def tick_reloj(self):
        self.lbl_reloj.setText(datetime.now().strftime("%H:%M:%S"))

    def guardado_automatico(self):
        self.guardar_datos()
        self.notificado.emit(
            "Guardado automatico {0}".format(datetime.now().strftime("%H:%M:%S"))
        )

    def keyPressEvent(self, evento):
        if self.hay_dialogo_abierto():
            super().keyPressEvent(evento)
            return

        if evento.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.calcular()
        elif evento.key() == Qt.Key_Escape:
            self.limpiar_todo()
        elif evento.key() == Qt.Key_Backspace:
            self.borrar_ultimo()
        else:
            super().keyPressEvent(evento)

    def hay_dialogo_abierto(self):
        return QApplication.activeModalWidget() is not None

    def mousePressEvent(self, evento):
        if evento.type() == QEvent.MouseButtonPress:
            if evento.button() == Qt.LeftButton and not self.hay_dialogo_abierto():
                self.statusBar().showMessage(
                    "Clic en {0},{1}".format(evento.pos().x(), evento.pos().y()), 2000
                )
        super().mousePressEvent(evento)

    def mouseDoubleClickEvent(self, evento):
        self.limpiar_entrada()
        self.notificado.emit("Doble clic: entrada limpia")
        super().mouseDoubleClickEvent(evento)

    def wheelEvent(self, evento):
        if self.hay_dialogo_abierto():
            super().wheelEvent(evento)
            return

        try:
            actual = float(self.lbl_resultado.text().replace("=", "").strip() or 0)
        except ValueError:
            actual = 0.0

        ctrl = bool(evento.modifiers() & Qt.ControlModifier)
        if ctrl:
            nuevo = -actual
        else:
            nuevo = actual * 1.1 if evento.angleDelta().y() > 0 else actual / 1.1

        self.lbl_resultado.setText("= {0}".format(self.formatear(nuevo)))
        self.notificado.emit(
            "Rueda {0}: {1}".format("Ctrl" if ctrl else "", self.formatear(nuevo))
        )

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self.lbl_subtitulo.setText(
            "{0}  ::  {1}x{2}  ::  F1 ayuda  ::  F2 ajustes  ::  doble clic limpia".format(
                TITULO, self.width(), self.height()
            )
        )

    def closeEvent(self, evento):
        self.guardar_datos()
        self.timer_reloj.stop()
        self.timer_guardado.stop()
        self.notificado.emit("Sesion cerrada. Datos guardados.")
        super().closeEvent(evento)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(TITULO)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()