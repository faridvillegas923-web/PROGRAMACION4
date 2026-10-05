import json
import math
import os
from datetime import datetime

import wx

ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculadora3_datos.json")
ARCHIVO_REPORTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculadora3_reporte.txt")

TITULO = "CALCULADORA CIENTIFICA"

FONDO = "#05060f"
PANEL = "#0b0f1e"

ACENTOS = ["#00f0ff", "#ff2bd6", "#39ff14", "#ff9f1c", "#7b5cff"]

MODOS = [("deg", "Grados"), ("rad", "Radianes"), ("grad", "Gradianes")]

TECLAS = [
    ("MC", "memoria", "Borra la memoria"),
    ("MR", "memoria", "Trae la memoria a la entrada"),
    ("M+", "memoria", "Suma el resultado a la memoria"),
    ("M-", "memoria", "Resta el resultado de la memoria"),
    ("CE", "limpiar", "Borra solo la entrada"),
    ("C", "limpiar", "Borra entrada y resultado"),
    ("(", "operador", "Abre parentesis"),
    (")", "operador", "Cierra parentesis"),
    ("%", "operador", "Porcentaje"),
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
    ("mod", "operador", "Modulo"),
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


def fuente(tamano=11, negrita=False):
    estilo = wx.FONTWEIGHT_BOLD if negrita else wx.FONTWEIGHT_NORMAL
    return wx.Font(tamano, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, estilo, False)


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


class DialogoBase(wx.Dialog):
    def __init__(self, padre, titulo, acento, ancho=430, alto=300):
        super().__init__(padre, title=titulo, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.padre = padre
        self.acento = acento
        self.SetBackgroundColour(FONDO)
        self.SetSize(ancho, alto)
        self.SetFont(fuente(10))

        raiz = wx.BoxSizer(wx.VERTICAL)
        self.lbl_titulo = wx.StaticText(self, label=titulo)
        self.lbl_titulo.SetFont(fuente(14, True))
        self.pintar(self.lbl_titulo)
        raiz.Add(self.lbl_titulo, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        self.cuerpo = wx.Panel(self)
        self.cuerpo.SetBackgroundColour(FONDO)
        raiz.Add(self.cuerpo, 1, wx.EXPAND | wx.ALL, 10)

        self.fila_botones = wx.BoxSizer(wx.HORIZONTAL)
        raiz.Add(self.fila_botones, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        self.SetSizer(raiz)

    def pintar(self, widget):
        widget.SetBackgroundColour(FONDO)
        widget.SetForegroundColour(self.acento)

    def texto(self, contenido, tamano=10):
        etiqueta = wx.StaticText(self.cuerpo, label=contenido)
        etiqueta.SetFont(fuente(tamano))
        self.pintar(etiqueta)
        return etiqueta

    def agregar_boton(self, texto, comando, principal=False):
        boton = wx.Button(self, label=texto, style=wx.BU_EXACTFIT)
        boton.SetFont(fuente(10, True))
        boton.SetForegroundColour(self.acento)
        boton.SetBackgroundColour(self.acento if principal else PANEL)
        boton.Bind(wx.EVT_BUTTON, comando)
        self.fila_botones.Add(boton, 0, wx.LEFT, 6)
        return boton


class HistorialDialog(DialogoBase):
    def __init__(self, padre, historial, acento):
        super().__init__(padre, "Historial de calculos", acento, 560, 470)
        self.historial = historial
        self.mayusculas = wx.CheckBox(self.cuerpo, label="Mayusculas")
        self.cientifico = wx.CheckBox(self.cuerpo, label="Notacion cientifica")
        self.tamanio = wx.ComboBox(
            self.cuerpo, choices=["Pequeno", "Normal", "Grande"], style=wx.CB_READONLY
        )
        self.tamanio.SetSelection(1)

        self.txt = wx.TextCtrl(
            self.cuerpo,
            value="",
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP | wx.HSCROLL,
        )
        self.pintar(self.txt)

        raiz = wx.BoxSizer(wx.VERTICAL)
        raiz.Add(self.txt, 1, wx.EXPAND | wx.ALL, 6)

        opciones = wx.BoxSizer(wx.HORIZONTAL)
        opciones.Add(self.mayusculas, 0, wx.ALL, 6)
        opciones.Add(self.cientifico, 0, wx.ALL, 6)
        opciones.AddStretchSpacer()
        opciones.Add(self.tamanio, 0, wx.ALL, 6)
        raiz.Add(opciones, 0, wx.EXPAND)

        self.cuerpo.SetSizer(raiz)

        for control in (self.mayusculas, self.cientifico):
            self.pintar(control)
            control.SetFont(fuente(10))
            control.Bind(wx.EVT_CHECKBOX, self.pintar_historial)
        self.tamanio.SetBackgroundColour(PANEL)
        self.tamanio.SetForegroundColour(acento)
        self.tamanio.Bind(wx.EVT_COMBOBOX, self.cambiar_tamanio)

        self.agregar_boton("CERRAR", self.Close, principal=True)
        self.pintar_historial()

    def cambiar_tamanio(self, _evento):
        tamanos = {"Pequeno": 9, "Normal": 11, "Grande": 14}
        self.txt.SetFont(fuente(tamanos.get(self.tamanio.GetStringSelection(), 11)))
        self.pintar_historial()

    def pintar_historial(self, _evento=None):
        lineas = []
        if not self.historial:
            lineas = ["Todavia no hay calculos guardados."]
        else:
            for indice, item in enumerate(self.historial, start=1):
                valor = item["resultado"]
                if self.cientifico.GetValue():
                    try:
                        valor = "{0:.6e}".format(float(valor))
                    except ValueError:
                        pass
                linea = "{0:02d}. {1} = {2}   [{3}]".format(
                    indice, bonito(item["expresion"]), valor, item.get("fecha", "")
                )
                lineas.append(linea.upper() if self.mayusculas.GetValue() else linea)

        self.txt.SetValue("\n".join(lineas))


class AcercaDeDialog(DialogoBase):
    def __init__(self, padre, acento):
        super().__init__(padre, "Acerca de {}".format(TITULO), acento, 480, 420)
        contenido = (
            "Calculadora cientifica con memoria, historial y\nevaluador de expresiones propio (sin eval).\n\n"
            "wxPython: wx.App, wx.Frame, wx.Panel, wx.Dialog,\n"
            "wx.Button, wx.TextCtrl, wx.ComboBox, wx.CheckBox,\n"
            "wx.SpinCtrl, wx.MenuBar, wx.Menu, wx.MenuItem,\n"
            "wx.RadioItem, wx.BoxSizer, wx.GridBagSizer,\n"
            "wx.StaticBox, wx.StaticText, wx.Timer, wx.MessageBox,\n"
            "wx.AcceleratorTable, portapapeles y eventos\n"
            "de teclado, raton, rueda y redimension.\n\n"
            "wxPython 4.3 sobre Python 3\n\n"
            "Fue echo por el echicero"
        )
        etiqueta = self.texto(contenido)
        etiqueta.SetFont(fuente(10))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(etiqueta, 1, wx.EXPAND | wx.ALL, 8)
        self.cuerpo.SetSizer(sizer)
        self.agregar_boton("CERRAR", self.Close, principal=True)


class AjustesDialog(DialogoBase):
    def __init__(self, padre, modo, decimales, guardar, panel, acento):
        super().__init__(padre, "Ajustes de la calculadora", acento, 440, 300)
        self.modo = wx.ComboBox(
            self.cuerpo, choices=[texto for _clave, texto in MODOS], style=wx.CB_READONLY
        )
        self.modo.SetSelection([clave for clave, _ in MODOS].index(modo))
        self.decimales = wx.SpinCtrl(self.cuerpo, min=0, max=10, initial=int(decimales))
        self.guardar = wx.CheckBox(self.cuerpo, label="Guardar los calculos en el historial")
        self.guardar.SetValue(guardar)
        self.panel = wx.CheckBox(self.cuerpo, label="Mostrar el panel de memoria")
        self.panel.SetValue(panel)

        grid = wx.FlexGridSizer(0, 2, 10, 10)
        grid.AddGrowableCol(1, 1)
        grid.Add(self.texto("Modo angular:"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.modo, 0, wx.EXPAND)
        grid.Add(self.texto("Decimales:"), 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(self.decimales, 0, wx.EXPAND)
        grid.AddSpacer(0)
        grid.Add(self.guardar, 0, wx.EXPAND)
        grid.AddSpacer(0)
        grid.Add(self.panel, 0, wx.EXPAND)
        grid.AddSpacer(0)
        grid.Add(self.texto("Se guardara al aceptar"), 0, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 10)
        self.cuerpo.SetSizer(sizer)

        for control in (self.guardar, self.panel):
            self.pintar(control)
            control.SetFont(fuente(10))
        self.modo.SetBackgroundColour(PANEL)
        self.modo.SetForegroundColour(acento)

        self.agregar_boton("GUARDAR", self.aceptar, principal=True)
        self.agregar_boton("CANCELAR", self.Close)

    def aceptar(self, _evento):
        indice = self.modo.GetSelection()
        clave = MODOS[indice][0] if 0 <= indice < len(MODOS) else "deg"
        self.padre.aplicar_ajustes(
            clave, self.decimales.GetValue(), self.guardar.GetValue(), self.panel.GetValue()
        )
        self.Close()


class VentanaPrincipal(wx.Frame):
    def __init__(self):
        super().__init__(None, title=TITULO, size=(1380, 780), style=wx.DEFAULT_FRAME_STYLE)

        self.acento = ACENTOS[0]
        self.modo = "deg"
        self.decimales = 6
        self.motor = Motor(self.modo)
        self.memoria = 0.0
        self.historial = []
        self.guardar_historial = True
        self.mostrar_panel = True
        self.parpadeo = True
        self.dialogo_actual = None
        self.cargar_datos()

        self.SetBackgroundColour(FONDO)
        self.SetFont(fuente(10))
        self.CreateStatusBar(1)

        self.crear_menu()
        self.crear_ui()
        self.crear_atajos()
        self.aplicar_tema()
        self.mostrar_memoria()
        self.mostrar_historial()

        self.timer_reloj = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.tick_reloj, self.timer_reloj)
        self.timer_reloj.Start(1000)

        self.timer_guardado = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.guardado_automatico, self.timer_guardado)
        self.timer_guardado.Start(30000)

        self.notificar(
            "{} lista. F1 ayuda :: F2 ajustes :: doble clic limpia".format(TITULO)
        )

    def crear_menu(self):
        barra = wx.MenuBar()

        archivo = wx.Menu()
        self.id_nuevo = archivo.Append(wx.ID_NEW, "Nuevo calculo\tCtrl+N", "Limpia la entrada").GetId()
        self.id_guardar = archivo.Append(wx.ID_SAVE, "Guardar\tCtrl+S", "Guarda en el disco").GetId()
        self.id_exportar = archivo.Append(wx.ID_ANY, "Exportar reporte\tCtrl+E").GetId()
        archivo.AppendSeparator()
        self.id_salir = archivo.Append(wx.ID_EXIT, "Salir\tCtrl+Q").GetId()
        barra.Append(archivo, "&Archivo")

        edicion = wx.Menu()
        self.id_copiar = edicion.Append(wx.ID_COPY, "Copiar resultado\tCtrl+C").GetId()
        self.id_pegar = edicion.Append(wx.ID_PASTE, "Pegar numero\tCtrl+V").GetId()
        self.id_borrar_historial = edicion.Append(
            wx.ID_ANY, "Borrar historial\tCtrl+Shift+B"
        ).GetId()
        edicion.AppendSeparator()
        self.id_ajustes = edicion.Append(wx.ID_ANY, "Ajustes\tF2").GetId()
        barra.Append(edicion, "&Editar")

        ver = wx.Menu()
        luz = wx.Menu()
        self.id_color = {}
        for color in ACENTOS:
            item = luz.AppendRadioItem(wx.ID_ANY, color, color)
            self.id_color[color] = item.GetId()
            ver.Bind(wx.EVT_MENU, self.al_elegir_color, item)
        ver.AppendSubMenu(luz, "Luz neon")
        ver.AppendSeparator()

        angular = wx.Menu()
        self.id_modo = {}
        for indice, (clave, texto) in enumerate(MODOS):
            item = angular.AppendRadioItem(wx.ID_ANY, "{0}\tCtrl+{1}".format(texto, indice + 1))
            self.id_modo[clave] = item.GetId()
            ver.Bind(wx.EVT_MENU, self.al_elegir_modo, item)
        ver.AppendSubMenu(angular, "Modo angular")
        ver.AppendSeparator()

        self.id_panel = ver.AppendCheckItem(wx.ID_ANY, "Ver panel de memoria\tCtrl+M").GetId()
        barra.Append(ver, "&Ver")

        calculadora = wx.Menu()
        rapidas = wx.Menu()
        self.id_rapida = []
        self.datos_rapida = {}
        for etiqueta, expresion in [
            ("Cuadrado del ultimo\tCtrl+U", "ans^2"),
            ("Raiz del ultimo\tCtrl+R", "√(ans)"),
            ("Inverso del ultimo\tCtrl+I", "1/ans"),
            ("Porcentaje del ultimo\tCtrl+P", "(ans/100)"),
        ]:
            item = rapidas.Append(wx.ID_ANY, etiqueta)
            rapidas.Bind(wx.EVT_MENU, self.al_escribir_menu, item)
            self.id_rapida.append(item.GetId())
            self.datos_rapida[item.GetId()] = expresion
        calculadora.AppendSubMenu(rapidas, "Operaciones rapidas")

        memoria = wx.Menu()
        self.id_memoria = []
        self.datos_memoria = {}
        for etiqueta, comando in [
            ("Limpiar memoria (MC)\tCtrl+Shift+M", "MC"),
            ("Traer memoria (MR)\tCtrl+Alt+M", "MR"),
            ("Sumar a la memoria (M+)\tCtrl+Alt+A", "M+"),
            ("Restar de la memoria (M-)\tCtrl+Alt+R", "M-"),
        ]:
            item = memoria.Append(wx.ID_ANY, etiqueta)
            memoria.Bind(wx.EVT_MENU, self.al_memoria_menu, item)
            self.id_memoria.append(item.GetId())
            self.datos_memoria[item.GetId()] = comando
        calculadora.AppendSubMenu(memoria, "Memoria")
        calculadora.AppendSeparator()
        self.id_calcular = calculadora.Append(wx.ID_ANY, "Calcular (Enter)").GetId()
        calculadora.Bind(wx.EVT_MENU, self.calcular, id=self.id_calcular)
        barra.Append(calculadora, "&Calculadora")

        ayuda = wx.Menu()
        self.id_atajos = ayuda.Append(wx.ID_HELP, "Atajos de teclado\tF1").GetId()
        self.id_funciones = ayuda.Append(wx.ID_ANY, "Funciones del motor").GetId()
        self.id_acerca = ayuda.Append(wx.ID_ABOUT, "Acerca de...").GetId()
        barra.Append(ayuda, "A&yuda")

        self.SetMenuBar(barra)
        self.barra = barra
        self.marcar_modos()

        eventos = [
            (self.id_nuevo, self.limpiar_todo),
            (self.id_guardar, self.guardar_datos),
            (self.id_exportar, self.exportar),
            (self.id_salir, self.cerrar),
            (self.id_copiar, self.copiar_resultado),
            (self.id_pegar, self.pegar_numero),
            (self.id_borrar_historial, self.limpiar_historial),
            (self.id_ajustes, self.abrir_ajustes),
            (self.id_panel, self.alternar_panel),
            (self.id_atajos, self.mostrar_atajos),
            (self.id_funciones, self.mostrar_funciones),
            (self.id_acerca, self.mostrar_acerca_de),
        ]
        for identificador, manejador in eventos:
            self.Bind(wx.EVT_MENU, manejador, id=identificador)

        self.Bind(wx.EVT_MENU_HIGHLIGHT, self.al_hover_menu)

    def al_escribir_menu(self, evento):
        self.escribir(self.datos_rapida.get(evento.GetId(), ""))
        evento.Skip()

    def al_memoria_menu(self, evento):
        self.operar_memoria(self.datos_memoria.get(evento.GetId(), ""))
        evento.Skip()

    def al_hover_menu(self, evento):
        elemento = self.barra.FindItemById(evento.GetId())
        if elemento is not None:
            self.SetStatusText(elemento.GetItemLabelText())

    def al_elegir_color(self, evento):
        self.cambiar_color(evento.GetId())
        evento.Skip()

    def marcar_modos(self):
        for clave, identificador in self.id_modo.items():
            self.barra.Check(identificador, clave == self.modo)
        for color, identificador in self.id_color.items():
            self.barra.Check(identificador, color == self.acento)
        self.barra.Check(self.id_panel, self.mostrar_panel)

    def crear_ui(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(FONDO)
        raiz = wx.BoxSizer(wx.VERTICAL)

        cabecera = wx.BoxSizer(wx.HORIZONTAL)
        self.lbl_titulo = wx.StaticText(panel, label=TITULO)
        self.lbl_titulo.SetFont(fuente(20, True))
        cabecera.Add(self.lbl_titulo, 1, wx.ALIGN_CENTER_VERTICAL)
        self.lbl_vivo = wx.StaticText(panel, label="EN VIVO")
        self.lbl_vivo.SetFont(fuente(10, True))
        cabecera.Add(self.lbl_vivo, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 8)
        self.lbl_reloj = wx.StaticText(panel, label="--:--:--")
        self.lbl_reloj.SetFont(fuente(16, True))
        cabecera.Add(self.lbl_reloj, 0, wx.ALIGN_CENTER_VERTICAL)
        raiz.Add(cabecera, 0, wx.EXPAND | wx.ALL, 8)

        self.lbl_subtitulo = wx.StaticText(
            panel, label="Menuus :: F1 ayuda :: F2 ajustes :: doble clic limpia"
        )
        self.lbl_subtitulo.SetFont(fuente(9))
        raiz.Add(self.lbl_subtitulo, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 8)

        cuerpo = wx.BoxSizer(wx.HORIZONTAL)
        self.crear_teclado(panel, cuerpo)
        self.crear_panel(panel, cuerpo)
        raiz.Add(cuerpo, 1, wx.EXPAND | wx.ALL, 8)

        pie = wx.StaticText(panel, label="Fue echo por el echicero")
        pie.SetFont(fuente(9))
        raiz.Add(pie, 0, wx.ALIGN_CENTER | wx.TOP, 6)

        self.lbl_estado = wx.StaticText(panel, label="Esperando datos...")
        self.lbl_estado.SetFont(fuente(9))
        raiz.Add(self.lbl_estado, 0, wx.ALIGN_CENTER | wx.ALL, 6)

        barra = wx.BoxSizer(wx.HORIZONTAL)
        self.lbl_modo = wx.StaticText(panel, label="MODO: GRADOS")
        self.lbl_modo.SetFont(fuente(10, True))
        barra.Add(self.lbl_modo, 0, wx.ALL, 6)
        self.lbl_operacion = wx.StaticText(panel, label="Listo")
        barra.Add(self.lbl_operacion, 1, wx.ALIGN_CENTER)
        self.lbl_ultimo = wx.StaticText(panel, label="Ultimo: -")
        self.lbl_ultimo.SetFont(fuente(10, True))
        barra.Add(self.lbl_ultimo, 0, wx.ALL, 6)
        raiz.Add(barra, 0, wx.EXPAND)

        panel.SetSizer(raiz)
        self.panel = panel

        panel.Bind(wx.EVT_LEFT_DCLICK, self.al_doble_clic)
        panel.Bind(wx.EVT_LEFT_DOWN, self.al_clic)
        panel.Bind(wx.EVT_MOUSEWHEEL, self.al_rueda)
        self.Bind(wx.EVT_MOUSEWHEEL, self.al_rueda)
        self.Bind(wx.EVT_SIZE, self.al_redimensionar)
        self.Bind(wx.EVT_CHAR_HOOK, self.al_tecla)
        self.Bind(wx.EVT_CLOSE, self.al_cerrar)

    def crear_teclado(self, padre, raiz):
        marco = wx.StaticBoxSizer(wx.StaticBox(padre, label="TECLADO"), wx.VERTICAL)
        cuerpo = marco.GetStaticBox()
        cuerpo.SetBackgroundColour(FONDO)

        self.lbl_memoria = wx.StaticText(cuerpo, label="M: 0", style=wx.ALIGN_RIGHT)
        self.lbl_memoria.SetFont(fuente(11, True))
        marco.Add(self.lbl_memoria, 0, wx.EXPAND | wx.ALL, 4)

        borde = wx.Panel(cuerpo)
        borde.SetBackgroundColour(self.acento)
        interior = wx.Panel(borde)
        interior.SetBackgroundColour(PANEL)
        self.txt_expresion = wx.TextCtrl(
            interior,
            value="",
            style=wx.TE_READONLY | wx.TE_RIGHT | wx.TE_DONTWRAP,
        )
        self.txt_expresion.SetFont(fuente(16, True))
        self.txt_expresion.SetBackgroundColour(PANEL)
        self.txt_expresion.SetForegroundColour(self.acento)

        self.lbl_resultado = wx.StaticText(interior, label="= 0", style=wx.ALIGN_RIGHT)
        self.lbl_resultado.SetFont(fuente(26, True))
        self.lbl_resultado.SetBackgroundColour(PANEL)
        self.lbl_resultado.SetForegroundColour(self.acento)

        dentro = wx.BoxSizer(wx.VERTICAL)
        dentro.Add(self.txt_expresion, 0, wx.EXPAND | wx.ALL, 6)
        dentro.Add(self.lbl_resultado, 0, wx.EXPAND | wx.ALL, 6)
        interior.SetSizer(dentro)

        marco.Add(borde, 0, wx.EXPAND | wx.ALL, 4)

        cuadricula = wx.GridBagSizer(4, 4)
        self.botones = {}
        for posicion, (etiqueta, clase, ayuda) in enumerate(TECLAS):
            boton = wx.Button(cuerpo, label=etiqueta, size=(92, 40))
            boton.SetFont(fuente(12 if clase == "numero" else 10, clase == "numero"))
            boton.SetForegroundColour(self.acento)
            boton.SetBackgroundColour(PANEL)
            boton.SetHelpText(ayuda)
            boton.Bind(wx.EVT_BUTTON, self.al_pulsar)
            boton.Bind(wx.EVT_ENTER_WINDOW, self.al_entrar_boton)

            fila = posicion // 6
            columna = posicion % 6
            if etiqueta == "=":
                cuadricula.Add(boton, pos=(fila, 4), span=(1, 2), flag=wx.EXPAND)
                columna = 4
            else:
                cuadricula.Add(boton, pos=(fila, columna), flag=wx.EXPAND)
            self.botones[etiqueta] = boton

        marco.Add(cuadricula, 1, wx.EXPAND | wx.ALL, 4)
        raiz.Add(marco, 3, wx.EXPAND | wx.RIGHT, 6)

    def crear_panel(self, padre, raiz):
        marco = wx.StaticBoxSizer(
            wx.StaticBox(padre, label="MEMORIA E HISTORIAL"), wx.VERTICAL
        )
        cuerpo = marco.GetStaticBox()
        cuerpo.SetBackgroundColour(FONDO)

        self.cmb_angulo = wx.ComboBox(
            cuerpo, choices=[texto for _clave, texto in MODOS], style=wx.CB_READONLY
        )
        self.cmb_angulo.SetSelection([clave for clave, _ in MODOS].index(self.modo))
        self.cmb_angulo.SetBackgroundColour(PANEL)
        self.cmb_angulo.SetForegroundColour(self.acento)
        self.cmb_angulo.Bind(wx.EVT_COMBOBOX, self.al_cambiar_modo)

        fila_modo = wx.BoxSizer(wx.HORIZONTAL)
        etiqueta_modo = wx.StaticText(cuerpo, label="Modo angular:")
        etiqueta_modo.SetFont(fuente(10))
        fila_modo.Add(etiqueta_modo, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
        fila_modo.Add(self.cmb_angulo, 1, wx.ALL, 4)
        marco.Add(fila_modo, 0, wx.EXPAND)

        self.ck_panel = wx.CheckBox(cuerpo, label="Ver panel")
        self.ck_panel.SetValue(True)
        self.ck_panel.Bind(wx.EVT_CHECKBOX, self.al_cambiar_panel)
        marco.Add(self.ck_panel, 0, wx.ALL, 6)

        self.ck_guardar = wx.CheckBox(cuerpo, label="Guardar historial")
        self.ck_guardar.SetValue(self.guardar_historial)
        self.ck_guardar.Bind(wx.EVT_CHECKBOX, self.al_cambiar_guardado)
        marco.Add(self.ck_guardar, 0, wx.ALL, 6)

        separador = wx.StaticLine(cuerpo)
        marco.Add(separador, 0, wx.EXPAND | wx.ALL, 8)

        self.lbl_contador = wx.StaticText(cuerpo, label="Calculos: 0")
        self.lbl_contador.SetFont(fuente(10, True))
        marco.Add(self.lbl_contador, 0, wx.ALL, 6)

        self.txt_historial = wx.TextCtrl(
            cuerpo, value="", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP
        )
        self.txt_historial.SetFont(fuente(10))
        self.txt_historial.SetBackgroundColour(PANEL)
        self.txt_historial.SetForegroundColour(self.acento)
        marco.Add(self.txt_historial, 1, wx.EXPAND | wx.ALL, 6)

        self.lbl_resumen = wx.StaticText(cuerpo, label="Memoria: 0")
        self.lbl_resumen.SetFont(fuente(9))
        marco.Add(self.lbl_resumen, 0, wx.ALL, 6)

        self.lbl_mensaje = wx.StaticText(cuerpo, label="Listo para calcular")
        self.lbl_mensaje.SetFont(fuente(9))
        marco.Add(self.lbl_mensaje, 0, wx.ALL, 6)

        self.botones_panel = {}
        textos = [
            ("HISTORIAL", self.ver_historial),
            ("AJUSTES", self.abrir_ajustes),
            ("COPIAR", self.copiar_resultado),
            ("EXPORTAR", self.exportar),
            ("LIMPIAR", self.limpiar_historial),
            ("NUEVO", self.limpiar_todo),
        ]
        for indice in range(0, len(textos), 2):
            fila = wx.BoxSizer(wx.HORIZONTAL)
            for texto, manejador in textos[indice:indice + 2]:
                boton = wx.Button(cuerpo, label=texto, size=(110, 32))
                boton.SetFont(fuente(10, True))
                boton.SetForegroundColour(self.acento)
                boton.SetBackgroundColour(PANEL)
                boton.Bind(wx.EVT_BUTTON, manejador)
                boton.Bind(wx.EVT_ENTER_WINDOW, self.al_entrar_boton)
                fila.Add(boton, 1, wx.ALL, 3)
                self.botones_panel[texto] = boton
            marco.Add(fila, 0, wx.EXPAND)

        raiz.Add(marco, 2, wx.EXPAND)

    def crear_atajos(self):
        atajos = [
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("N"), self.id_nuevo),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("S"), self.id_guardar),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("E"), self.id_exportar),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("Q"), self.id_salir),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("C"), self.id_copiar),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("V"), self.id_pegar),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord("M"), self.id_panel),
            wx.AcceleratorEntry(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord("B"), self.id_borrar_historial),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F1, self.id_atajos),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F2, self.id_ajustes),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_RETURN, self.id_calcular),
            wx.AcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_NUMPAD_ENTER, self.id_calcular),
        ]
        for posicion, tecla in enumerate("URIP"):
            atajos.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord(tecla), self.id_rapida[posicion]))
        atajos.extend(
            [
                wx.AcceleratorEntry(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord("M"), self.id_memoria[0]),
                wx.AcceleratorEntry(wx.ACCEL_CTRL | wx.ACCEL_ALT, ord("M"), self.id_memoria[1]),
                wx.AcceleratorEntry(wx.ACCEL_CTRL | wx.ACCEL_ALT, ord("A"), self.id_memoria[2]),
                wx.AcceleratorEntry(wx.ACCEL_CTRL | wx.ACCEL_ALT, ord("R"), self.id_memoria[3]),
            ]
        )
        for indice, (clave, _texto) in enumerate(MODOS):
            atajos.append(
                wx.AcceleratorEntry(wx.ACCEL_CTRL, ord(str(indice + 1)), self.id_modo[clave])
            )
        self.SetAcceleratorTable(wx.AcceleratorTable(atajos))

    def pintar(self, widget):
        widget.SetBackgroundColour(FONDO)
        widget.SetForegroundColour(self.acento)

    def aplicar_tema(self):
        self.SetBackgroundColour(FONDO)
        barra = self.GetStatusBar()
        if barra is not None:
            barra.SetBackgroundColour(PANEL)
            barra.SetForegroundColour(self.acento)
        self.pintar(self.lbl_titulo)
        self.pintar(self.lbl_vivo)
        self.pintar(self.lbl_reloj)
        self.pintar(self.lbl_subtitulo)
        self.pintar(self.lbl_estado)
        self.pintar(self.lbl_modo)
        self.pintar(self.lbl_operacion)
        self.pintar(self.lbl_ultimo)
        self.pintar(self.lbl_memoria)
        self.pintar(self.lbl_resultado)
        self.pintar(self.lbl_contador)
        self.pintar(self.lbl_resumen)
        self.pintar(self.lbl_mensaje)
        self.lbl_resultado.SetBackgroundColour(PANEL)

        for etiqueta in ("lbl_memoria", "lbl_contador", "lbl_modo", "lbl_ultimo"):
            getattr(self, etiqueta).SetFont(fuente(11, True))

        self.txt_expresion.SetForegroundColour(self.acento)
        self.txt_historial.SetForegroundColour(self.acento)
        self.cmb_angulo.SetForegroundColour(self.acento)

        self.botones["="].SetBackgroundColour(self.acento)
        self.botones["="].SetForegroundColour(FONDO)
        self.botones["C"].SetBackgroundColour(self.acento)
        self.botones["C"].SetForegroundColour(FONDO)

        for caja in (self.ck_panel, self.ck_guardar):
            caja.SetBackgroundColour(FONDO)
            caja.SetForegroundColour(self.acento)

        for boton in list(self.botones.values()) + list(self.botones_panel.values()):
            boton.SetForegroundColour(self.acento)
            if boton is not self.botones["="] and boton is not self.botones["C"]:
                boton.SetBackgroundColour(PANEL)

        self.marcar_modos()
        self.Layout()

    def formatear(self, valor):
        return formatear(valor, self.decimales)

    def texto_modo(self):
        for clave, texto in MODOS:
            if clave == self.modo:
                return texto
        return "Grados"

    def al_pulsar(self, evento):
        self.pulsar(evento.GetEventObject().GetLabel())

    def al_entrar_boton(self, evento):
        boton = evento.GetEventObject()
        if boton.GetHelpText():
            self.notificar(boton.GetHelpText())

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
        actual = self.txt_expresion.GetValue()
        valor = texto.startswith(
            ("sin(", "cos(", "tan(", "ln(", "log(", "exp(", "√(", "abs(", "pi", "e", "(", "1/(", "ans")
        )
        if actual and valor and (
            actual[-1:].isdigit() or actual[-1:] in ".)" or actual.endswith("!")
        ):
            actual += "*"
        for simbolo, ascii_ in (("×", "*"), ("÷", "/"), ("−", "-")):
            texto = texto.replace(simbolo, ascii_)
        nuevo = actual + texto
        self.txt_expresion.ChangeValue(nuevo)
        self.txt_expresion.SetInsertionPointEnd()
        self.lbl_operacion.SetLabel("Expresion: {0}".format(bonito(nuevo)))

    def cerrar_parentesis(self, texto):
        faltan = texto.count("(") - texto.count(")")
        if faltan > 0:
            texto += ")" * faltan
        return texto

    def borrar_ultimo(self):
        texto = self.txt_expresion.GetValue()
        self.txt_expresion.ChangeValue(texto[:-1])

    def cambiar_signo(self):
        texto = self.txt_expresion.GetValue()
        self.txt_expresion.ChangeValue(texto[1:] if texto.startswith("-") else "-" + texto)

    def limpiar_entrada(self):
        self.txt_expresion.ChangeValue("")
        self.lbl_resultado.SetLabel("= 0")
        self.notificar("Entrada limpia")

    def limpiar_todo(self):
        self.limpiar_entrada()
        self.motor.ultimo = 0.0
        self.lbl_ultimo.SetLabel("Ultimo: -")
        self.notificar("Calculadora reiniciada")

    def calcular(self, _evento=None):
        texto = self.cerrar_parentesis(self.txt_expresion.GetValue().strip())
        if not texto:
            self.notificar("Escribe algo antes de calcular")
            return

        try:
            valor = self.motor.evaluar(texto)
        except ErrorCalculo as error:
            self.notificar("Error: {0}".format(error))
            wx.MessageBox(str(error), "No se pudo calcular", wx.OK | wx.ICON_WARNING, self)
            return
        except Exception:
            self.notificar("Error: expresion no valida")
            wx.MessageBox("La expresion no es valida.", "No se pudo calcular", wx.OK | wx.ICON_WARNING, self)
            return

        if valor != valor or valor in (float("inf"), float("-inf")):
            self.notificar("Error: resultado indefinido")
            wx.MessageBox("El resultado no existe.", "No se pudo calcular", wx.OK | wx.ICON_WARNING, self)
            return

        resultado = self.formatear(valor)
        self.lbl_resultado.SetLabel("= {0}".format(resultado))
        self.lbl_ultimo.SetLabel("Ultimo: {0}".format(resultado))
        self.txt_expresion.ChangeValue(resultado)
        self.lbl_operacion.SetLabel("Resultado: {0}".format(resultado))
        self.SetStatusText("Resultado: {0}".format(resultado))

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

    def operar_memoria(self, comando, _evento=None):
        actual = self.motor.ultimo
        if comando == "MC":
            self.memoria = 0.0
            self.notificar("Memoria borrada")
        elif comando == "MR":
            self.escribir(self.formatear(self.memoria))
            self.notificar("Memoria: {0}".format(self.formatear(self.memoria)))
            return
        elif comando == "M+":
            self.memoria += actual
            self.notificar("Memoria: {0}".format(self.formatear(self.memoria)))
        elif comando == "M-":
            self.memoria -= actual
            self.notificar("Memoria: {0}".format(self.formatear(self.memoria)))

        self.mostrar_memoria()
        self.guardar_datos()

    def mostrar_memoria(self):
        self.lbl_memoria.SetLabel("M: {0}".format(self.formatear(self.memoria)))
        self.lbl_resumen.SetLabel(
            "Memoria: {0} | Calculos: {1}".format(self.formatear(self.memoria), len(self.historial))
        )

    def mostrar_historial(self):
        if not self.historial:
            self.txt_historial.SetValue("Todavia no hay calculos.")
        else:
            self.txt_historial.SetValue(
                "\n".join(
                    "{0:02d}. {1} = {2}".format(
                        indice, bonito(item["expresion"]), item["resultado"]
                    )
                    for indice, item in enumerate(self.historial[:60], start=1)
                )
            )
        self.lbl_contador.SetLabel("Calculos: {0}".format(len(self.historial)))
        self.mostrar_memoria()

    def notificar(self, mensaje):
        self.lbl_estado.SetLabel(mensaje)
        self.lbl_mensaje.SetLabel(mensaje)
        self.SetStatusText(mensaje)

    def ver_historial(self, _evento=None):
        dialogo = HistorialDialog(self, self.historial, self.acento)
        self.abrir_modal(dialogo)

    def abrir_modal(self, dialogo):
        self.dialogo_actual = dialogo
        try:
            dialogo.ShowModal()
        finally:
            self.dialogo_actual = None
            dialogo.Destroy()

    def limpiar_historial(self, _evento=None):
        if not self.historial:
            wx.MessageBox("El historial ya esta vacio.", "Aviso", wx.OK | wx.ICON_INFORMATION, self)
            return
        respuesta = wx.MessageBox(
            "Borrar todos los calculos?", "Borrar historial", wx.YES_NO | wx.ICON_QUESTION, self
        )
        if respuesta == wx.YES:
            self.historial = []
            self.mostrar_historial()
            self.guardar_datos()
            self.notificar("Historial borrado")

    def abrir_ajustes(self, _evento=None):
        dialogo = AjustesDialog(
            self, self.modo, self.decimales, self.guardar_historial, self.mostrar_panel, self.acento
        )
        self.abrir_modal(dialogo)

    def aplicar_ajustes(self, modo, decimales, guardar, panel):
        self.cambiar_modo(modo)
        self.decimales = decimales
        self.guardar_historial = guardar
        self.mostrar_panel = panel
        self.ck_guardar.SetValue(guardar)
        self.ck_panel.SetValue(panel)
        self.al_cambiar_panel()
        self.guardar_datos()
        self.notificar("Ajustes guardados")
        self.Layout()

    def copiar_resultado(self, _evento=None):
        resultado = self.lbl_resultado.GetLabel().replace("=", "").strip()
        if resultado in ("", "0"):
            wx.MessageBox(
                "No hay ningun resultado que copiar.", "Aviso", wx.OK | wx.ICON_INFORMATION, self
            )
            return
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(resultado))
            wx.TheClipboard.Close()
        self.notificar("Copiado: {0}".format(resultado))

    def pegar_numero(self, _evento=None):
        texto = ""
        datos = wx.TextDataObject()
        if wx.TheClipboard.Open():
            if wx.TheClipboard.GetData(datos):
                texto = datos.GetText()
            wx.TheClipboard.Close()
        limpio = "".join(c for c in texto.strip() if c.isdigit() or c in ".,-")
        if not limpio:
            wx.MessageBox(
                "El portapapeles no tiene numeros.", "Aviso", wx.OK | wx.ICON_INFORMATION, self
            )
            return
        self.escribir(limpio.replace(",", "."))
        self.notificar("Pegado: {0}".format(limpio))

    def exportar(self, _evento=None):
        if not self.historial:
            wx.MessageBox(
                "No hay calculos para exportar.", "Aviso", wx.OK | wx.ICON_INFORMATION, self
            )
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
            archivo.write("Memoria actual: {0}\n".format(self.formatear(self.memoria)))

        wx.MessageBox(
            "Reporte guardado en:\n{0}".format(ARCHIVO_REPORTE), "Exportar", wx.OK, self
        )
        self.notificar("Reporte exportado en {0}".format(ARCHIVO_REPORTE))

    def guardar_datos(self, _evento=None):
        datos = {
            "historial": self.historial,
            "memoria": self.memoria,
            "modo": self.modo,
            "acento": self.acento,
            "guardar_historial": self.guardar_historial,
        }
        try:
            with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=2, ensure_ascii=False)
        except OSError as error:
            self.notificar("No se pudo guardar: {0}".format(error))

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
        self.acento = datos.get("acento", ACENTOS[0])
        self.guardar_historial = bool(datos.get("guardar_historial", True))
        if self.modo not in [clave for clave, _ in MODOS]:
            self.modo = "deg"
        if self.acento not in ACENTOS:
            self.acento = ACENTOS[0]
        self.motor.angulo = self.modo

    def al_elegir_modo(self, evento):
        for clave, identificador in self.id_modo.items():
            if identificador == evento.GetId():
                self.cambiar_modo(clave)
                break
        evento.Skip()

    def cambiar_modo(self, modo):
        if modo not in [clave for clave, _ in MODOS]:
            modo = "deg"
        self.modo = modo
        self.motor.angulo = modo
        indice = [clave for clave, _ in MODOS].index(modo)
        self.cmb_angulo.SetSelection(indice)
        self.lbl_modo.SetLabel("MODO: {0}".format(self.texto_modo().upper()))
        self.marcar_modos()
        self.notificar("Modo angular: {0}".format(self.texto_modo().lower()))

    def cambiar_color(self, identificador):
        for color, item in self.id_color.items():
            if item == identificador:
                self.acento = color
                break
        self.aplicar_tema()
        self.notificar("Luz neon cambiada a {0}".format(self.acento))

    def al_cambiar_modo(self, evento):
        indice = self.cmb_angulo.GetSelection()
        self.cambiar_modo(MODOS[indice][0] if 0 <= indice < len(MODOS) else "deg")
        evento.Skip()

    def al_cambiar_panel(self, evento=None):
        self.mostrar_panel = self.ck_panel.GetValue()
        self.txt_historial.Show(self.mostrar_panel)
        self.lbl_mensaje.Show(self.mostrar_panel)
        self.lbl_resumen.Show(self.mostrar_panel)
        self.marcar_modos()
        self.Layout()
        if evento is not None:
            evento.Skip()

    def al_cambiar_guardado(self, evento):
        self.guardar_historial = self.ck_guardar.GetValue()
        self.notificar(
            "Historial {0}".format("activado" if self.guardar_historial else "desactivado")
        )
        evento.Skip()

    def alternar_panel(self, _evento=None):
        self.ck_panel.SetValue(not self.mostrar_panel)
        self.al_cambiar_panel()

    def mostrar_atajos(self, _evento=None):
        dialogo = DialogoBase(self, "Atajos de teclado", self.acento, 480, 400)
        texto = (
            "Enter        Calcular el resultado\n"
            "Esc          Borrar la entrada\n"
            "BackSpace    Borrar el ultimo caracter\n"
            "Ctrl+N       Nuevo calculo\n"
            "Ctrl+S       Guardar en el disco\n"
            "Ctrl+E       Exportar reporte\n"
            "Ctrl+C       Copiar el resultado\n"
            "Ctrl+V       Pegar un numero\n"
            "Ctrl+M       Mostrar u ocultar el panel\n"
            "Ctrl+1/2/3   Grados, radianes, gradianes\n"
            "Ctrl+R       Raiz del ultimo resultado\n"
            "Ctrl+U       Cuadrado del ultimo resultado\n"
            "Ctrl+I       Inverso del ultimo resultado\n"
            "Ctrl+Shift+B Borrar el historial\n"
            "F1           Esta ayuda\n"
            "F2           Ajustes\n"
            "Doble clic   Limpia la entrada\n"
            "Rueda        Ajusta el resultado en 10%"
        )
        etiqueta = dialogo.texto(texto)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(etiqueta, 1, wx.EXPAND | wx.ALL, 8)
        dialogo.cuerpo.SetSizer(sizer)
        dialogo.agregar_boton("CERRAR", dialogo.Close, principal=True)
        self.abrir_modal(dialogo)

    def mostrar_funciones(self, _evento=None):
        dialogo = DialogoBase(self, "Funciones del motor", self.acento, 470, 400)
        texto = (
            "trigonometricas\n"
            "  sin(x) cos(x) tan(x) en el modo angular elegido\n"
            "  asin(x) acos(x) atan(x) devuelven el modo angular\n"
            "logaritmos\n"
            "  ln(x) logaritmo natural\n"
            "  log(x) logaritmo base 10\n"
            "potencias y raices\n"
            "  x^y potencia, boton x2 para el cuadrado\n"
            "  raiz(x) raiz cuadrada, exp(x) e elevado a x\n"
            "  n! factorial de 0 a 170\n"
            "otras\n"
            "  abs(x) valor absoluto\n"
            "  mod (%) resto de la division\n"
            "  pi y e constantes, ans ultimo resultado\n"
            "ejemplo: sin(30)+cos(60)*2"
        )
        etiqueta = dialogo.texto(texto)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(etiqueta, 1, wx.EXPAND | wx.ALL, 8)
        dialogo.cuerpo.SetSizer(sizer)
        dialogo.agregar_boton("CERRAR", dialogo.Close, principal=True)
        self.abrir_modal(dialogo)

    def mostrar_acerca_de(self, _evento=None):
        dialogo = AcercaDeDialog(self, self.acento)
        self.abrir_modal(dialogo)

    def tick_reloj(self, _evento=None):
        self.lbl_reloj.SetLabel(datetime.now().strftime("%H:%M:%S"))
        self.parpadeo = not self.parpadeo
        self.lbl_vivo.SetForegroundColour(self.acento if self.parpadeo else "#1c2233")

    def guardado_automatico(self, evento):
        self.guardar_datos()
        self.notificar("Guardado automatico {0}".format(datetime.now().strftime("%H:%M:%S")))

    def al_tecla(self, evento):
        codigo = evento.GetKeyCode()
        if codigo in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self.calcular()
        elif codigo == wx.WXK_ESCAPE:
            self.limpiar_todo()
        elif codigo == wx.WXK_BACK:
            self.borrar_ultimo()
        else:
            evento.Skip()

    def al_clic(self, evento):
        posicion = evento.GetPosition()
        self.lbl_operacion.SetLabel("Clic en {0},{1}".format(posicion.x, posicion.y))

    def al_doble_clic(self, evento):
        self.limpiar_entrada()
        self.notificar("Doble clic: entrada limpia")
        evento.Skip()

    def al_rueda(self, evento):
        try:
            actual = float(self.lbl_resultado.GetLabel().replace("=", "").strip() or 0)
        except ValueError:
            actual = 0.0
        if evento.ControlDown():
            nuevo = -actual
            texto = "Ctrl"
        else:
            nuevo = actual * 1.1 if evento.GetWheelRotation() > 0 else actual / 1.1
            texto = "Rueda"
        self.lbl_resultado.SetLabel("= {0}".format(self.formatear(nuevo)))
        self.notificar("{0}: {1}".format(texto, self.formatear(nuevo)))

    def al_redimensionar(self, evento):
        self.lbl_subtitulo.SetLabel(
            "{0}  ::  {1}x{2}  ::  F1 ayuda  ::  F2 ajustes  ::  doble clic limpia".format(
                TITULO, evento.GetSize().x, evento.GetSize().y
            )
        )
        evento.Skip()

    def al_cerrar(self, evento):
        self.guardar_datos()
        self.timer_reloj.Stop()
        self.timer_guardado.Stop()
        self.notificar("Sesion cerrada. Datos guardados.")
        self.Destroy()

    def cerrar(self, _evento=None):
        self.Close()


def main():
    app = wx.App(False)
    ventana = VentanaPrincipal()
    ventana.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()