import json
import math
import os
import re
import sys
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QKeySequence
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

ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculadora2_datos.json")
ARCHIVO_REPORTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculadora2_reporte.txt")

TITULO = "CALCULADORA CIENTIFICA"

MODOS = [("deg", "Grados"), ("rad", "Radianes"), ("grad", "Gradianes")]

LIMITE_RECIENTES = 5

NUMERO_FINAL = re.compile(r"^(.*?)(\d+\.\d+|\d+|\.\d+)$")

PERMITIDOS = set("0123456789.,+-*/^%()! √πabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

TECLAS = [
    ("MC", "memoria", "Borra la memoria (MC)"),
    ("MR", "memoria", "Recupera la memoria (MR)"),
    ("M+", "memoria", "Suma el resultado a la memoria"),
    ("M-", "memoria", "Resta el resultado de la memoria"),
    ("CE", "limpiar", "Borra solo la entrada actual"),
    ("C", "limpiar", "Borra entrada y resultado"),
    ("(", "operador", "Abre parentesis"),
    (")", "operador", "Cierra parentesis"),
    ("%", "operador", "Porcentaje (divide entre 100)"),
    ("÷", "operador", "Division"),
    ("x^y", "operador", "Potencia"),
    ("⌫", "borrar", "Borra el ultimo caracter"),
    ("7", "numero", "Siete"),
    ("8", "numero", "Ocho"),
    ("9", "numero", "Nueve"),
    ("×", "operador", "Multiplicacion"),
    ("√", "operador", "Raiz cuadrada"),
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
    ("±", "operador", "Cambia el signo"),
    ("mod", "operador", "Modulo (resto)"),
    ("|x|", "operador", "Valor absoluto"),
    ("1/x", "operador", "Inverso"),
    ("n!", "operador", "Factorial"),
    ("asin", "operador", "Arcoseno"),
    ("acos", "operador", "Arcocoseno"),
    ("atan", "operador", "Arcotangente"),
    ("=", "operador", "Calcula el resultado"),
    ("ans", "operador", "Escribe el ultimo resultado (ans)"),
]

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
    padding: 7px 6px;
    color: #1c1c1c;
    font-weight: bold;
}
QPushButton:hover { background-color: #eaeaea; border-color: #8f8f8f; }
QPushButton:pressed { background-color: #d6d6d6; }
QPushButton:disabled { background-color: #e8e8e8; color: #a8a8a8; border-color: #d2d2d2; }
QPushButton#numero { background-color: #ffffff; font-size: 15px; }
QPushButton#numero:hover { background-color: #f0f4fa; }
QPushButton#operador { background-color: #e4e4e4; }
QPushButton#memoria { background-color: #e8eef7; color: #24476b; }
QPushButton#limpiar { background-color: #f0e6e6; color: #7a2f2f; }
QPushButton#borrar { background-color: #f0e6e6; color: #7a2f2f; }
QPushButton#igual { background-color: #2f6fd0; color: #ffffff; font-size: 16px; }
QPushButton#igual:hover { background-color: #3d7ce0; }
QPushButton#reciente {
    background-color: #ffffff;
    text-align: left;
    padding: 6px 10px;
    font-weight: normal;
}
QPushButton#reciente:hover { background-color: #eaf1fb; }
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
                tokens.append("%" if nombre == "mod" else nombre)
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
        self.resize(620, 460)
        self.setStyleSheet(TEMA)

        encabezado = QLabel("CALCULOS REALIZADOS")
        encabezado.setFont(QFont("Segoe UI", 12, QFont.Bold))
        encabezado.setAlignment(Qt.AlignCenter)

        self.txt_filtro = QLineEdit()
        self.txt_filtro.setPlaceholderText("Buscar en el historial...")
        self.txt_filtro.textChanged.connect(self.pintar)

        self.txt_historial = QTextEdit()
        self.txt_historial.setReadOnly(True)

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

        self.lbl_resumen = QLabel("")
        self.lbl_resumen.setAlignment(Qt.AlignRight)

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(self.reject)
        botones.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(encabezado)
        layout.addWidget(self.txt_filtro)
        layout.addWidget(self.txt_historial, 1)
        layout.addWidget(self.lbl_resumen)
        layout.addLayout(opciones)
        layout.addLayout(forma)
        layout.addWidget(botones)

        self.pintar()

    def cambiar_tamanio(self, indice):
        self.txt_historial.setFont(QFont("Consolas", [10, 11, 14][indice]))

    def pintar(self):
        if not self.historial:
            self.txt_historial.setPlainText("Todavia no hay calculos guardados.")
            self.lbl_resumen.setText("0 calculos")
            return

        cientifico = self.rb_cientifico.isChecked()
        mayusculas = self.ck_mayusculas.isChecked()
        filtro = self.txt_filtro.text().strip().lower()

        lineas = []
        for indice, item in enumerate(self.historial, start=1):
            valor = item["resultado"]
            if cientifico:
                try:
                    valor = "{0:.6e}".format(float(valor))
                except ValueError:
                    pass
            linea = "{0:03d}. {1} = {2}   [{3}]".format(
                indice, bonito(item["expresion"]), valor, item.get("fecha", "")
            )
            if filtro and filtro not in linea.lower():
                continue
            lineas.append(linea.upper() if mayusculas else linea)

        if not lineas:
            self.txt_historial.setPlainText("Ningun calculo coincide con el filtro.")
        else:
            self.txt_historial.setPlainText("\n".join(lineas))

        self.lbl_resumen.setText("{0} de {1} calculos".format(len(lineas), len(self.historial)))


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
        self.ck_panel = QCheckBox("Mostrar el panel de memoria")
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


class TextoDialog(QDialog):
    def __init__(self, parent=None, titulo="", encabezado="", contenido=""):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setMinimumWidth(470)
        self.setStyleSheet(TEMA)

        self.lbl_titulo = QLabel(encabezado)
        self.lbl_titulo.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.lbl_titulo.setAlignment(Qt.AlignCenter)

        self.txt_texto = QTextEdit()
        self.txt_texto.setReadOnly(True)
        self.txt_texto.setPlainText(contenido)

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(self.reject)
        botones.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.txt_texto, 1)
        layout.addWidget(botones)


class VentanaPrincipal(QMainWindow):
    notificado = pyqtSignal(str)
    calculado = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(TITULO)
        self.setStyleSheet(TEMA)
        self.resize(1120, 760)

        self.modo = "deg"
        self.decimales = 6
        self.motor = Motor(self.modo)
        self.memoria = 0.0
        self.historial = []
        self.recientes = []
        self.borrador = ""
        self.guardar_historial = True
        self.mostrar_panel = True
        self.ver_recientes = True
        self.restaurando = False
        self.pila_undo = []
        self.texto_previo = ""
        self.cargar_datos()

        self.crear_ui()
        self.crear_menus()
        self.mostrar_memoria()
        self.mostrar_historial()
        self.mostrar_recientes()
        if self.borrador:
            self.aplicar_texto(self.borrador)

        self.notificado.connect(self.mostrar_notificacion)
        self.calculado.connect(self.al_terminar_calculo)

        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.tick_reloj)
        self.timer_reloj.start(1000)

        self.timer_guardado = QTimer(self)
        self.timer_guardado.timeout.connect(self.guardado_automatico)
        self.timer_guardado.start(30000)

        self.notificado.emit(
            "{} lista. Escribe con el teclado :: F1 ayuda :: F2 ajustes".format(TITULO)
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

        self.lbl_subtitulo = QLabel(
            "Menuus :: F1 ayuda :: F2 ajustes :: clic en una operacion para reutilizarla"
        )
        self.lbl_subtitulo.setObjectName("rotulo")
        self.lbl_subtitulo.setAlignment(Qt.AlignCenter)
        raiz.addWidget(self.lbl_subtitulo)

        cuerpo = QHBoxLayout()
        raiz.addLayout(cuerpo, 1)

        izquierda = QVBoxLayout()
        derecha = QVBoxLayout()
        cuerpo.addLayout(izquierda, 5)
        cuerpo.addLayout(derecha, 3)

        izquierda.addWidget(self.crear_teclado())
        izquierda.addWidget(self.crear_recientes())
        derecha.addWidget(self.crear_panel())

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

    def crear_teclado(self):
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
        self.txt_expresion.setAlignment(Qt.AlignRight)
        self.txt_expresion.setPlaceholderText("Escribe o usa las teclas...")
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
            boton.setMinimumHeight(38)
            if clase == "numero":
                boton.setFont(QFont("Segoe UI", 14, QFont.Bold))
            boton.clicked.connect(lambda _c=False, t=etiqueta: self.pulsar(t))
            self.botones[etiqueta] = boton
            cuadricula.addWidget(boton, posicion // 6, posicion % 6)

        layout.addLayout(cuadricula, 1)
        return grupo

    def crear_recientes(self):
        grupo = QGroupBox("ULTIMAS {0} OPERACIONES".format(LIMITE_RECIENTES))
        self.grupo_recientes = grupo
        layout = QVBoxLayout(grupo)

        ayuda = QLabel("Haz clic en una operacion para copiarla a la entrada")
        ayuda.setObjectName("rotulo")
        ayuda.setAlignment(Qt.AlignCenter)
        layout.addWidget(ayuda)

        self.botones_recientes = []
        for posicion in range(LIMITE_RECIENTES):
            boton = QPushButton("{0}. --".format(posicion + 1))
            boton.setObjectName("reciente")
            boton.setEnabled(False)
            boton.setMinimumHeight(30)
            boton.clicked.connect(lambda _c=False, i=posicion: self.reutilizar_operacion(i))
            layout.addWidget(boton)
            self.botones_recientes.append(boton)

        return grupo

    def crear_panel(self):
        grupo = QGroupBox("MEMORIA E HISTORIAL")
        layout = QVBoxLayout(grupo)

        self.cmb_angulo = QComboBox()
        for clave, texto in MODOS:
            self.cmb_angulo.addItem(texto, clave)
        self.cmb_angulo.setCurrentIndex([clave for clave, _ in MODOS].index(self.modo))
        self.cmb_angulo.currentIndexChanged.connect(self.al_cambiar_modo)

        self.ck_panel = QCheckBox("Ver panel")
        self.ck_panel.setChecked(self.mostrar_panel)
        self.ck_panel.stateChanged.connect(self.al_cambiar_panel)

        self.ck_guardar = QCheckBox("Guardar historial")
        self.ck_guardar.setChecked(self.guardar_historial)
        self.ck_guardar.stateChanged.connect(self.al_cambiar_guardado)

        formulario = QFormLayout()
        formulario.addRow("Modo angular:", self.cmb_angulo)
        formulario.addRow("Panel:", self.ck_panel)
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
        self.txt_historial.setVisible(self.mostrar_panel)
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
        self.btn_limpiar = QPushButton("LIMPIAR")
        self.btn_ajustes = QPushButton("AJUSTES")
        self.btn_copiar = QPushButton("COPIAR")
        self.btn_exportar = QPushButton("EXPORTAR")
        self.btn_nuevo = QPushButton("NUEVO")

        self.btn_historial.clicked.connect(self.ver_historial)
        self.btn_limpiar.clicked.connect(self.limpiar_historial)
        self.btn_ajustes.clicked.connect(self.abrir_ajustes)
        self.btn_copiar.clicked.connect(self.copiar_resultado)
        self.btn_exportar.clicked.connect(self.exportar)
        self.btn_nuevo.clicked.connect(self.limpiar_todo)

        primera = QHBoxLayout()
        primera.addWidget(self.btn_historial)
        primera.addWidget(self.btn_ajustes)
        layout.addLayout(primera)

        segunda = QHBoxLayout()
        segunda.addWidget(self.btn_copiar)
        segunda.addWidget(self.btn_exportar)
        layout.addLayout(segunda)

        tercera = QHBoxLayout()
        tercera.addWidget(self.btn_limpiar)
        tercera.addWidget(self.btn_nuevo)
        layout.addLayout(tercera)

        return grupo

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
        self.agregar_accion(
            archivo, "&Nuevo calculo", QKeySequence.New,
            "Limpia la entrada para empezar de cero", self.limpiar_todo
        )
        self.agregar_accion(
            archivo, "&Guardar", QKeySequence.Save,
            "Guarda memoria, historial y ajustes en el disco", self.guardar_datos
        )
        self.agregar_accion(
            archivo, "&Exportar reporte...", "Ctrl+E",
            "Exporta el historial a un archivo de texto", self.exportar
        )
        archivo.addSeparator()
        self.agregar_accion(
            archivo, "&Salir", "Ctrl+Q", "Cierra la calculadora", self.close
        )

        edicion = barra.addMenu("&Editar")
        self.agregar_accion(
            edicion, "&Deshacer", QKeySequence.Undo, "Revierte el ultimo cambio en la entrada",
            self.deshacer
        )
        self.agregar_accion(
            edicion, "&Copiar resultado", QKeySequence.Copy,
            "Copia el resultado al portapapeles", self.copiar_resultado
        )
        self.agregar_accion(
            edicion, "&Pegar numero", QKeySequence.Paste,
            "Pega un numero desde el portapapeles", self.pegar_numero
        )
        self.agregar_accion(
            edicion, "&Borrar historial", "Ctrl+Shift+B",
            "Borra todos los calculos guardados", self.limpiar_historial
        )
        edicion.addSeparator()
        self.agregar_accion(
            edicion, "&Ajustes...", "F2", "Modo angular, decimales y paneles",
            self.abrir_ajustes
        )

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

        accion = QAction("Mostrar &panel de memoria", self, checkable=True)
        accion.setChecked(self.mostrar_panel)
        accion.setShortcut("Ctrl+M")
        accion.setStatusTip("Muestra u oculta el panel lateral")
        accion.triggered.connect(self.alternar_panel)
        ver.addAction(accion)
        self.acciones["panel"] = accion

        accion = QAction(
            "Mostrar &ultimas {0} operaciones".format(LIMITE_RECIENTES), self, checkable=True
        )
        accion.setChecked(self.ver_recientes)
        accion.setShortcut("Ctrl+L")
        accion.setStatusTip("Muestra u oculta el historial corto")
        accion.triggered.connect(self.alternar_recientes)
        ver.addAction(accion)
        self.acciones["recientes"] = accion

        calculadora = barra.addMenu("&Calculadora")
        menu_rapidas = calculadora.addMenu("Operaciones rapidas")
        for etiqueta, expresion, atajo in [
            ("Cuadrado del ultimo", "ans^2", "Ctrl+U"),
            ("Raiz del ultimo", "√(ans)", "Ctrl+R"),
            ("Inverso del ultimo", "1/ans", "Ctrl+I"),
            ("Porcentaje del ultimo", "(ans/100)", "Ctrl+P"),
        ]:
            self.agregar_accion(
                menu_rapidas, etiqueta, atajo, "Escribe {0} en la entrada".format(expresion),
                lambda _v=False, e=expresion: self.escribir(e)
            )

        menu_memoria = calculadora.addMenu("Memoria")
        for etiqueta, comando, atajo in [
            ("Limpiar memoria (MC)", "MC", "Ctrl+Shift+M"),
            ("Traer memoria (MR)", "MR", "Ctrl+Alt+M"),
            ("Sumar a la memoria (M+)", "M+", "Ctrl+Alt+A"),
            ("Restar de la memoria (M-)", "M-", "Ctrl+Alt+R"),
        ]:
            self.agregar_accion(
                menu_memoria, etiqueta, atajo, etiqueta,
                lambda _v=False, c=comando: self.operar_memoria(c)
            )

        calculadora.addSeparator()
        self.agregar_accion(
            calculadora, "Calcular (&=)", "Return",
            "Evalua la expresion de la entrada", self.calcular
        )
        self.agregar_accion(
            calculadora, "Borrar entrada (Esc)", "Escape",
            "Limpia la entrada", self.limpiar_entrada
        )
        self.agregar_accion(
            calculadora, "Borrar caracter (Retroceso)", "Backspace",
            "Borra el ultimo caracter", self.borrar_ultimo
        )
        self.agregar_accion(
            calculadora, "&Reutilizar ultima operacion", "Ctrl+Shift+U",
            "Pone el resultado de la ultima operacion en la entrada",
            lambda: self.reutilizar_operacion(0)
        )

        ayuda = barra.addMenu("A&yuda")
        self.agregar_accion(
            ayuda, "&Atajos de teclado...", "F1", "Muestra la lista de atajos",
            self.mostrar_atajos
        )
        self.agregar_accion(
            ayuda, "&Funciones disponibles...", None,
            "Lista de funciones del motor de calculo", self.mostrar_funciones
        )
        self.agregar_accion(
            ayuda, "&Acerca de...", None, "Informacion del sistema", self.mostrar_acerca_de
        )

        for accion in self.findChildren(QAction):
            accion.hovered.connect(self.al_hover_accion)

    def agregar_accion(self, menu, texto, atajo, ayuda, ranura):
        accion = QAction(texto, self)
        if atajo is not None:
            accion.setShortcut(atajo)
        accion.setStatusTip(ayuda)
        accion.triggered.connect(ranura)
        menu.addAction(accion)
        return accion

    # --------------------------------------------------------------- calculadora

    def formatear(self, valor):
        return formatear(valor, self.decimales)

    def texto_modo(self):
        for clave, texto in MODOS:
            if clave == self.modo:
                return texto
        return "Grados"

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
            self.envolver_operando("1/(")
        elif etiqueta == "n!":
            self.escribir("!")
        elif etiqueta == "|x|":
            self.envolver_operando("abs(")
        elif etiqueta == "mod":
            self.escribir("%")
        elif etiqueta == "%":
            self.escribir("/100")
        elif etiqueta == "±":
            self.cambiar_signo()
        elif etiqueta == "√":
            self.envolver_operando("√(")
        elif etiqueta == "π":
            self.escribir("pi")
        elif etiqueta == "ans":
            self.escribir("ans")
        elif etiqueta in ("asin", "acos", "atan", "sin", "cos", "tan", "ln", "log", "exp"):
            self.envolver_operando(etiqueta + "(")
        elif etiqueta == "e":
            self.escribir("e")
        else:
            self.escribir(etiqueta)

    def envolver_operando(self, prefijo):
        texto = self.txt_expresion.text().rstrip()
        if not texto:
            self.escribir(prefijo)
            return
        if texto[-1] == ")":
            self.aplicar_texto("{0}({1})".format(prefijo, texto))
            return
        coincidencia = NUMERO_FINAL.match(texto)
        if coincidencia:
            self.aplicar_texto(
                "{0}{1}({2})".format(coincidencia.group(1), prefijo, coincidencia.group(2))
            )
            return
        self.escribir(prefijo)

    def reemplazar_operando_final(self, texto_nuevo):
        texto = self.txt_expresion.text().rstrip()
        if not texto:
            self.aplicar_texto(texto_nuevo)
            return
        if texto[-1] == ")":
            self.aplicar_texto("{0}({1})".format(texto_nuevo, texto))
            return
        coincidencia = NUMERO_FINAL.match(texto)
        if coincidencia:
            self.aplicar_texto("{0}{1}".format(coincidencia.group(1), texto_nuevo))
            return
        self.escribir(texto_nuevo)

    def aplicar_texto(self, texto, registrar=True, cursor_al_final=True):
        if registrar and texto != self.texto_previo:
            self.pila_undo.append(self.texto_previo)
            del self.pila_undo[200:]
        self.restaurando = True
        self.txt_expresion.setText(texto)
        if cursor_al_final:
            self.txt_expresion.setCursorPosition(len(texto))
        self.restaurando = False
        self.texto_previo = texto

    def escribir(self, texto):
        actual = self.txt_expresion.text()
        valor = texto.startswith(("sin(", "cos(", "tan(", "ln(", "log(", "exp(", "pi", "e", "(", "ans"))
        if actual and valor and (
            actual[-1:].isdigit() or actual[-1:] in ".)" or actual.endswith("!")
        ):
            actual += "*"
        for simbolo, ascii_ in (("×", "*"), ("÷", "/"), ("−", "-")):
            texto = texto.replace(simbolo, ascii_)
        self.aplicar_texto(actual + texto)

    def cerrar_parentesis(self, texto):
        faltan = texto.count("(") - texto.count(")")
        if faltan > 0:
            texto += ")" * faltan
        return texto

    def borrar_ultimo(self):
        self.aplicar_texto(self.txt_expresion.text()[:-1])

    def deshacer(self):
        if not self.pila_undo:
            self.notificado.emit("No hay nada que deshacer")
            return
        self.aplicar_texto(self.pila_undo.pop(), registrar=False)
        self.notificado.emit("Cambio deshecho")

    def cambiar_signo(self):
        texto = self.txt_expresion.text()
        if texto.startswith("-"):
            self.aplicar_texto(texto[1:])
        else:
            self.aplicar_texto("-" + texto)

    def limpiar_entrada(self):
        self.aplicar_texto("")
        self.lbl_resultado.setText("= 0")
        self.lbl_operacion.setText("Entrada limpia")

    def limpiar_todo(self):
        self.limpiar_entrada()
        self.motor.ultimo = 0.0
        self.lbl_ultimo.setText("Ultimo: -")
        self.notificado.emit("Calculadora reiniciada")

    def al_texto_cambiado(self, texto):
        limpio = "".join("." if c == "," else c for c in texto if c in PERMITIDOS)
        if not self.restaurando:
            if limpio != self.texto_previo:
                self.pila_undo.append(self.texto_previo)
                del self.pila_undo[200:]
            self.texto_previo = limpio
            if limpio != texto:
                self.restaurando = True
                self.txt_expresion.setText(limpio)
                self.txt_expresion.setCursorPosition(len(limpio))
                self.restaurando = False
        self.lbl_operacion.setText("Expresion: {0}".format(bonito(limpio) or "vacia"))

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
        self.aplicar_texto(resultado)
        self.calculado.emit(resultado)

        self.registrar_operacion(texto, resultado)

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

    def registrar_operacion(self, expresion, resultado):
        self.recientes.insert(
            0,
            {
                "expresion": expresion,
                "resultado": resultado,
                "fecha": datetime.now().strftime("%H:%M:%S"),
            },
        )
        del self.recientes[LIMITE_RECIENTES:]
        self.mostrar_recientes()

    def reutilizar_operacion(self, indice):
        if indice >= len(self.recientes):
            return
        item = self.recientes[indice]
        self.aplicar_texto("")
        self.escribir(item["resultado"])
        self.notificado.emit(
            "Operacion {0} reutilizada: {1}".format(indice + 1, item["resultado"])
        )

    def mostrar_recientes(self):
        for posicion, boton in enumerate(self.botones_recientes):
            if posicion < len(self.recientes):
                item = self.recientes[posicion]
                boton.setText(
                    "{0}. {1} = {2}".format(
                        posicion + 1, bonito(item["expresion"]), item["resultado"]
                    )
                )
                boton.setToolTip(
                    "{0} = {1}   [{2}]\nClic: lleva el resultado a la entrada".format(
                        bonito(item["expresion"]), item["resultado"], item.get("fecha", "")
                    )
                )
                boton.setStatusTip(boton.toolTip())
                boton.setEnabled(True)
            else:
                boton.setText("{0}. --".format(posicion + 1))
                boton.setToolTip("Todavia no hay operaciones aqui")
                boton.setStatusTip("")
                boton.setEnabled(False)
        self.grupo_recientes.setVisible(self.ver_recientes)

    def operar_memoria(self, etiqueta):
        actual = self.motor.ultimo

        if etiqueta == "MC":
            self.memoria = 0.0
            self.notificado.emit("Memoria borrada")
        elif etiqueta == "MR":
            self.reemplazar_operando_final(self.formatear(self.memoria))
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
            "Memoria: {0} | Calculos: {1} | Recientes: {2}/{3}".format(
                self.formatear(self.memoria),
                len(self.historial),
                len(self.recientes),
                LIMITE_RECIENTES,
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

    # ------------------------------------------------------------------ utiles

    def mostrar_notificacion(self, mensaje):
        self.lbl_estado.setText(mensaje)
        if hasattr(self, "lbl_mensaje"):
            self.lbl_mensaje.setText(mensaje)

    def al_terminar_calculo(self, resultado):
        self.statusBar().showMessage("Resultado: {0}".format(resultado), 3000)

    def ver_historial(self):
        HistorialDialog(self, self.historial).exec_()

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
        self.ck_panel.setChecked(panel)
        self.al_cambiar_panel()
        self.guardar_datos()
        self.notificado.emit("Ajustes guardados")

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

    def copiar_resultado(self):
        resultado = self.lbl_resultado.text().replace("=", "").strip()
        if not resultado:
            QMessageBox.information(self, "Aviso", "No hay ningun resultado que copiar.")
            return
        QApplication.clipboard().setText(resultado)
        self.notificado.emit("Copiado: {0}".format(resultado))

    def pegar_numero(self):
        texto = QApplication.clipboard().text().strip()
        limpio = "".join(c for c in texto if c.isdigit() or c in ".,-")
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
            archivo.write("Ultimas {0} operaciones:\n".format(LIMITE_RECIENTES))
            for posicion, item in enumerate(self.recientes, start=1):
                archivo.write(
                    "  {0}. {1} = {2} | {3}\n".format(
                        posicion, item["expresion"], item["resultado"], item.get("fecha", "")
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
        self.borrador = self.txt_expresion.text()
        datos = {
            "historial": self.historial,
            "recientes": self.recientes[:LIMITE_RECIENTES],
            "memoria": self.memoria,
            "modo": self.modo,
            "decimales": self.decimales,
            "guardar_historial": self.guardar_historial,
            "mostrar_panel": self.mostrar_panel,
            "expresion": self.borrador,
        }
        try:
            with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=2, ensure_ascii=False)
        except OSError as error:
            self.notificado.emit("No se pudo guardar: {0}".format(error))

    def cargar_datos(self):
        if not os.path.exists(ARCHIVO_DATOS):
            return
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (json.JSONDecodeError, OSError):
            return

        self.historial = datos.get("historial", [])[:200]
        self.recientes = datos.get("recientes", [])[:LIMITE_RECIENTES]
        self.memoria = float(datos.get("memoria", 0.0) or 0.0)
        self.modo = datos.get("modo", "deg")
        self.guardar_historial = bool(datos.get("guardar_historial", True))
        self.mostrar_panel = bool(datos.get("mostrar_panel", True))
        self.borrador = str(datos.get("expresion", "") or "")
        try:
            self.decimales = int(datos.get("decimales", self.decimales))
        except (TypeError, ValueError):
            self.decimales = 6
        if self.modo not in [clave for clave, _ in MODOS]:
            self.modo = "deg"
        self.motor.angulo = self.modo

    # ------------------------------------------------------------- modo y panel

    def cambiar_modo(self, modo):
        if modo not in [clave for clave, _ in MODOS]:
            modo = "deg"
        self.modo = modo
        self.motor.angulo = modo
        self.cmb_angulo.blockSignals(True)
        self.cmb_angulo.setCurrentIndex([clave for clave, _ in MODOS].index(modo))
        self.cmb_angulo.blockSignals(False)
        for posicion, (clave, _texto) in enumerate(MODOS):
            self.acciones["modo_{0}".format(posicion)].setChecked(clave == modo)
        self.lbl_modo.setText("MODO: {0}".format(self.texto_modo().upper()))

    def al_cambiar_modo(self, _indice):
        self.cambiar_modo(self.cmb_angulo.currentData())

    def al_elegir_modo(self):
        accion = self.sender()
        self.cambiar_modo(accion.data())
        self.notificado.emit("Modo angular: {0}".format(self.texto_modo()))

    def al_cambiar_panel(self, _estado=None):
        self.mostrar_panel = self.ck_panel.isChecked()
        self.lbl_mensaje.setVisible(self.mostrar_panel)
        self.txt_historial.setVisible(self.mostrar_panel)

    def al_cambiar_guardado(self, _estado):
        self.guardar_historial = self.ck_guardar.isChecked()
        self.notificado.emit(
            "Historial {0}".format("activado" if self.guardar_historial else "desactivado")
        )

    def alternar_panel(self):
        self.ck_panel.setChecked(not self.ck_panel.isChecked())

    def alternar_recientes(self, _v=False):
        self.ver_recientes = self.acciones["recientes"].isChecked()
        self.grupo_recientes.setVisible(self.ver_recientes)

    def al_hover_accion(self, _marcado=False):
        accion = self.sender()
        if accion is None:
            return
        self.statusBar().showMessage(accion.statusTip() or accion.text())

    # ----------------------------------------------------------------- timers

    def tick_reloj(self):
        self.lbl_reloj.setText(datetime.now().strftime("%H:%M:%S"))

    def guardado_automatico(self):
        self.guardar_datos()
        self.statusBar().showMessage(
            "Guardado automatico {0}".format(datetime.now().strftime("%H:%M:%S")), 3000
        )

    # ------------------------------------------------------------------ ayuda

    def mostrar_atajos(self):
        TextoDialog(
            self,
            "Atajos de teclado",
            "ATAJOS DE TECLADO",
            "Escribe        En la entrada (numeros, + - * / ^ ( ) y funciones)\n"
            "Coma o punto   Decimal (la coma se cambia sola a punto)\n"
            "Enter          Calcular el resultado\n"
            "Esc            Borrar la entrada\n"
            "Retroceso      Borrar el ultimo caracter\n"
            "Ctrl+Z         Deshacer el ultimo cambio\n"
            "Boton ans      Escribe el ultimo resultado (ans)\n"
            "Ctrl+N         Nuevo calculo\n"
            "Ctrl+S         Guardar en el disco\n"
            "Ctrl+E         Exportar reporte\n"
            "Ctrl+C         Copiar el resultado\n"
            "Ctrl+V         Pegar un numero\n"
            "Ctrl+M         Mostrar u ocultar el panel\n"
            "Ctrl+L         Mostrar u ocultar las ultimas 5\n"
            "Ctrl+1/2/3     Grados, radianes, gradianes\n"
            "Ctrl+R         Raiz del ultimo resultado\n"
            "Ctrl+U         Cuadrado del ultimo resultado\n"
            "Ctrl+I         Inverso del ultimo resultado\n"
            "Ctrl+Shift+U   Reutilizar la ultima operacion\n"
            "Ctrl+Shift+B   Borrar el historial\n"
            "F1             Esta ayuda\n"
            "F2             Ajustes\n"
            "Clic           Reutiliza una operacion reciente",
        ).exec_()

    def mostrar_funciones(self):
        TextoDialog(
            self,
            "Funciones del motor",
            "FUNCIONES DEL MOTOR",
            "trigonometricas\n"
            "  sin(x) cos(x) tan(x) en el modo angular elegido\n"
            "  asin(x) acos(x) atan(x) devuelven el modo angular\n"
            "logaritmos\n"
            "  ln(x) logaritmo natural\n"
            "  log(x) logaritmo base 10\n"
            "potencias y raices\n"
            "  x^y potencia, boton x2 para el cuadrado\n"
            "  √(x) raiz cuadrada, exp(x) e elevado a x\n"
            "  n! factorial de 0 a 170\n"
            "otras\n"
            "  abs(x) valor absoluto\n"
            "  mod (%) resto de la division\n"
            "  pi y e constantes, ans ultimo resultado\n"
            "ejemplo: sin(30)+cos(60)*2",
        ).exec_()

    def mostrar_acerca_de(self):
        TextoDialog(
            self,
            "Acerca de {}".format(TITULO),
            TITULO,
            "Calculadora cientifica con memoria, historial de las\n"
            "ultimas {0} operaciones y evaluador de expresiones\n"
            "propio (sin eval).\n\n"
            "PyQt5: QApplication, QMainWindow, QWidget, QDialog,\n"
            "QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,\n"
            "QCheckBox, QRadioButton, QGroupBox, QGridLayout,\n"
            "QFormLayout, QVBoxLayout, QHBoxLayout, QFrame,\n"
            "QDialogButtonBox, QMessageBox, QAction, QActionGroup,\n"
            "QMenuBar, QTimer, señales/slots y eventos de teclado.\n\n"
            "PyQt5 sobre Python 3\n\n"
            "Fue echo por el echicero".format(LIMITE_RECIENTES),
        ).exec_()

    def closeEvent(self, evento):
        self.guardar_datos()
        self.timer_reloj.stop()
        self.timer_guardado.stop()
        evento.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(TITULO)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()