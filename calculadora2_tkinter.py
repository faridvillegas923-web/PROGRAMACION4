import json
import math
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculadora2_datos.json")
ARCHIVO_REPORTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculadora2_reporte.txt")

TITULO = "CALCULADORA CIENTIFICA"

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


class VentanaDialogo(tk.Toplevel):
    def __init__(self, padre, titulo, acento, ancho=430, alto=None):
        super().__init__(padre)
        self.padre = padre
        self.acento = acento
        self.title(titulo)
        self.configure(bg="#05060f")
        self.resizable(False, False)
        self.transient(padre)
        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.ancho = ancho
        self.alto = alto

        self.lbl_titulo = tk.Label(
            self,
            text=titulo,
            bg="#05060f",
            fg=acento,
            font=("Consolas", 13, "bold"),
            pady=8,
        )
        self.lbl_titulo.pack(fill="x")

        self.cuerpo = ttk.Frame(self, padding=12)
        self.cuerpo.pack(fill="both", expand=True)

        self.fila_botones = ttk.Frame(self, padding=(12, 0, 12, 12))
        self.fila_botones.pack(fill="x")

        self.bind("<Escape>", lambda _e: self.cerrar())
        self.after(60, self.centrar)

    def centrar(self):
        try:
            x = self.padre.winfo_rootx() + (self.padre.winfo_width() - self.ancho) // 2
            y = self.padre.winfo_rooty() + (self.padre.winfo_height() - 260) // 2
            self.geometry("{0}x{1}+{2}+{3}".format(self.ancho, self.alto or 260, x, y))
        except tk.TclError:
            pass

    def agregar_boton(self, texto, comando):
        boton = ttk.Button(self.fila_botones, text=texto, command=comando)
        boton.pack(side="right", padx=4)
        return boton

    def cerrar(self):
        self.padre.dialogo_abierto = None
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()


class HistorialDialog(VentanaDialogo):
    def __init__(self, padre, historial, acento):
        super().__init__(padre, "Historial de calculos", acento, ancho=540, alto=460)
        self.historial = historial
        self.resizable(True, True)

        self.txt = tk.Text(
            self.cuerpo,
            bg="#0b0f1e",
            fg=acento,
            insertbackground=acento,
            relief="flat",
            font=("Consolas", 11),
            width=52,
            height=18,
            wrap="none",
        )
        self.txt.pack(fill="both", expand=True)

        self.mayusculas = tk.IntVar(value=0)
        self.cientifico = tk.IntVar(value=0)

        opciones = ttk.Frame(self.cuerpo)
        opciones.pack(fill="x", pady=(8, 0))
        ttk.Checkbutton(
            opciones, text="Mayusculas", variable=self.mayusculas, command=self.pintar
        ).pack(side="left")
        ttk.Checkbutton(
            opciones, text="Notacion cientifica", variable=self.cientifico, command=self.pintar
        ).pack(side="left", padx=10)

        self.tamanio = ttk.Combobox(
            opciones, values=["Pequeno", "Normal", "Grande"], width=10, state="readonly"
        )
        self.tamanio.set("Normal")
        self.tamanio.bind("<<ComboboxSelected>>", self.cambiar_tamanio)
        self.tamanio.pack(side="right")

        self.agregar_boton("CERRAR", self.cerrar)
        self.pintar()

    def cambiar_tamanio(self, _evento=None):
        tamanos = {"Pequeno": 9, "Normal": 11, "Grande": 14}
        self.txt.configure(font=("Consolas", tamanos.get(self.tamanio.get(), 11)))
        self.pintar()

    def pintar(self):
        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        if not self.historial:
            self.txt.insert("end", "Todavia no hay calculos guardados.")
        else:
            for indice, item in enumerate(self.historial, start=1):
                valor = item["resultado"]
                if self.cientifico.get():
                    try:
                        valor = "{0:.6e}".format(float(valor))
                    except ValueError:
                        pass
                linea = "{0:02d}. {1} = {2}   [{3}]\n".format(
                    indice, bonito(item["expresion"]), valor, item.get("fecha", "")
                )
                self.txt.insert("end", linea.upper() if self.mayusculas.get() else linea)
        self.txt.config(state="disabled")


class AcercaDeDialog(VentanaDialogo):
    def __init__(self, padre, acento):
        super().__init__(padre, "Acerca de {}".format(TITULO), acento, ancho=460, alto=380)
        ttk.Label(
            self.cuerpo,
            text=TITULO,
            font=("Consolas", 18, "bold"),
            foreground=acento,
            justify="center",
        ).pack(pady=(0, 10))

        texto = (
            "Calculadora cientifica con memoria, historial y\nevaluador de expresiones propio (sin eval).\n\n"
            "Tkinter: Tk, Toplevel, Frame, Label, Entry, Text,\n"
            "Button, Checkbutton, Combobox, Menu, ttk.Style,\n"
            "messagebox, after() como temporizador, bind() de\n"
            "teclado y raton, clipboard, grid() y pack().\n\n"
            "Python 3 - modulo tkinter\n\n"
            "Fue echo por el echicero"
        )
        tk.Label(
            self.cuerpo,
            text=texto,
            bg="#05060f",
            fg=acento,
            font=("Consolas", 10),
            justify="left",
        ).pack(fill="both", expand=True)

        self.agregar_boton("CERRAR", self.cerrar)


class AjustesDialog(VentanaDialogo):
    def __init__(self, padre, modo, decimales, guardar, panel, acento):
        super().__init__(padre, "Ajustes de la calculadora", acento, ancho=430, alto=250)

        self.modo = tk.StringVar(value=modo)
        self.decimales = tk.StringVar(value=str(decimales))
        self.guardar = tk.BooleanVar(value=guardar)
        self.panel = tk.BooleanVar(value=panel)

        formulario = ttk.Frame(self.cuerpo)
        formulario.pack(fill="x")

        ttk.Label(formulario, text="Modo angular:").grid(row=0, column=0, sticky="w", pady=6)
        combo = ttk.Combobox(
            formulario,
            textvariable=self.modo,
            values=[texto for _clave, texto in MODOS],
            state="readonly",
            width=18,
        )
        combo.grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(formulario, text="Decimales:").grid(row=1, column=0, sticky="w", pady=6)
        combo_dec = ttk.Combobox(
            formulario,
            textvariable=self.decimales,
            values=[str(n) for n in range(0, 11)],
            state="readonly",
            width=18,
        )
        combo_dec.grid(row=1, column=1, padx=8, pady=6)

        ttk.Checkbutton(
            formulario, text="Guardar los calculos en el historial", variable=self.guardar
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=6)
        ttk.Checkbutton(
            formulario, text="Mostrar el panel de memoria", variable=self.panel
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=6)

        ttk.Label(
            formulario,
            text="Modo actual: {0}   Decimales: {1}".format(modo, decimales),
            foreground=acento,
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))

        self.agregar_boton("GUARDAR", self.aceptar)
        self.agregar_boton("CANCELAR", self.cerrar)

    def aceptar(self):
        clave = "deg"
        for codigo, texto in MODOS:
            if texto == self.modo.get():
                clave = codigo
        self.padre.aplicar_ajustes(
            clave, int(self.decimales.get()), self.guardar.get(), self.panel.get()
        )
        self.cerrar()


class Calculadora(tk.Tk):
    def __init__(self):
        super().__init__()

        self.acento = ACENTOS[0]
        self.modo = "deg"
        self.decimales = 6
        self.motor = Motor(self.modo)
        self.memoria = 0.0
        self.historial = []
        self.guardar_historial = True
        self.mostrar_panel = True
        self.parpadeo = True
        self.dialogo_abierto = None

        self.var_modo = tk.StringVar(value=self.modo)
        self.var_color = tk.StringVar(value=self.acento)
        self.var_panel = tk.BooleanVar(value=True)
        self.var_guardar = tk.BooleanVar(value=True)
        self.var_decimales = tk.StringVar(value=str(self.decimales))
        self.var_operacion = tk.StringVar(value="Listo")
        self.var_reloj = tk.StringVar(value="--:--:--")
        self.var_modo_texto = tk.StringVar(value="MODO: GRADOS")
        self.var_ultimo = tk.StringVar(value="Ultimo: -")
        self.var_contador = tk.StringVar(value="Calculos: 0")
        self.var_resumen = tk.StringVar(value="Memoria: 0")
        self.var_mensaje = tk.StringVar(value="Listo para calcular")

        self.cargar_datos()

        self.title(TITULO)
        self.geometry("1300x760")
        self.minsize(1060, 660)
        self.configure(bg="#05060f")
        self.protocol("WM_DELETE_WINDOW", self.cerrar)

        self.aplicar_tema()
        self.crear_menu()
        self.crear_ui()
        self.crear_atajos()
        self.cambiar_modo(self.modo)
        self.mostrar_memoria()
        self.mostrar_historial()
        self.al_cambiar_panel()

        self.after(1000, self.tick_reloj)
        self.after(30000, self.guardado_automatico)

        self.notificar(
            "{} lista. F1 ayuda :: F2 ajustes :: doble clic limpia".format(TITULO)
        )

    def aplicar_tema(self):
        self.acento = self.var_color.get()
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        fondo, panel = "#05060f", "#0b0f1e"
        acento = self.acento

        self.configure(bg=fondo)
        self.style.configure(".", background=fondo, foreground=acento, font=("Consolas", 10))
        self.style.configure("TFrame", background=fondo)
        self.style.configure("Panel.TFrame", background=panel)
        self.style.configure("TLabel", background=fondo, foreground=acento)
        self.style.configure(
            "Neon.TLabel",
            background=fondo,
            foreground=acento,
            font=("Consolas", 20, "bold"),
            borderwidth=2,
            relief="solid",
        )
        self.style.configure("Titulo.TLabel", font=("Consolas", 20, "bold"))
        self.style.configure("Sub.TLabel", font=("Consolas", 9), foreground="#7d8aa8")
        self.style.configure("Result.TLabel", font=("Consolas", 26, "bold"), foreground=acento)
        self.style.configure("Memoria.TLabel", font=("Consolas", 11, "bold"))
        self.style.configure("Estado.TLabel", font=("Consolas", 10, "bold"))
        self.style.configure("Pie.TLabel", font=("Consolas", 9), foreground="#7d8aa8")

        self.style.configure(
            "TButton",
            background=panel,
            foreground=acento,
            bordercolor=acento,
            lightcolor=acento,
            darkcolor=acento,
            relief="solid",
            borderwidth=1,
            padding=6,
            font=("Consolas", 10, "bold"),
        )
        self.style.map(
            "TButton",
            background=[("active", acento)],
            foreground=[("active", fondo)],
        )
        self.style.configure("Numero.TButton", font=("Consolas", 12, "bold"))
        self.style.configure("Igual.TButton", background=acento, foreground=fondo)
        self.style.map("Igual.TButton", background=[("active", "#ffffff")])

        self.style.configure(
            "TCombobox",
            fieldbackground=panel,
            background=panel,
            foreground=acento,
            arrowcolor=acento,
            bordercolor=acento,
        )
        self.style.configure(
            "TCheckbutton", background=fondo, foreground=acento, indicatorcolor=panel
        )
        self.style.map("TCheckbutton", background=[("active", fondo)])
        self.style.configure("TSeparator", background=acento)
        self.style.configure("Vertical.TScrollbar", background=panel, troughcolor=fondo)
        self.style.configure(
            "Menu.TFrame",
            background=panel,
            borderwidth=1,
            relief="solid",
        )
        self.style.configure("TLabelframe", background=fondo, bordercolor=acento,
                             lightcolor=acento, darkcolor=acento, borderwidth=1)
        self.style.configure("TLabelframe.Label", foreground=acento, font=("Consolas", 10, "bold"))
        self.style.configure("Panel.TLabel", background=panel, foreground=acento,
                             font=("Consolas", 26, "bold"))
        self.style.configure("Vivo.TLabel", background=fondo, foreground=acento)

        if hasattr(self, "menu"):
            self.config(menu=self.menu)
            for menu in self.submenus:
                menu.configure(
                    bg="#0b0f1e",
                    fg=self.acento,
                    activebackground=self.acento,
                    activeforeground="#05060f",
                )

    def nuevo_menu(self, padre=None):
        menu = tk.Menu(
            padre or self,
            bg="#0b0f1e",
            fg=self.acento,
            activebackground=self.acento,
            activeforeground="#05060f",
            borderwidth=1,
            relief="solid",
            tearoff=0,
            font=("Consolas", 10),
        )
        if not hasattr(self, "submenus"):
            self.submenus = []
        self.submenus.append(menu)
        return menu

    def crear_menu(self):
        self.submenus = []
        self.menu = self.nuevo_menu(self)

        archivo = self.nuevo_menu()
        archivo.add_command(label="Nuevo calculo\tCtrl+N", command=self.limpiar_todo)
        archivo.add_command(label="Guardar\tCtrl+S", command=self.guardar_datos)
        archivo.add_command(label="Exportar reporte\tCtrl+E", command=self.exportar)
        archivo.add_separator()
        archivo.add_command(label="Salir\tCtrl+Q", command=self.cerrar)
        self.menu.add_cascade(label="Archivo", menu=archivo)

        edicion = self.nuevo_menu()
        edicion.add_command(label="Copiar resultado\tCtrl+C", command=self.copiar_resultado)
        edicion.add_command(label="Pegar numero\tCtrl+V", command=self.pegar_numero)
        edicion.add_command(label="Borrar historial\tCtrl+Shift+B", command=self.limpiar_historial)
        edicion.add_separator()
        edicion.add_command(label="Ajustes\tF2", command=self.abrir_ajustes)
        self.menu.add_cascade(label="Editar", menu=edicion)

        ver = self.nuevo_menu()
        luz = self.nuevo_menu()
        for color in ACENTOS:
            luz.add_radiobutton(
                label=color,
                variable=self.var_color,
                value=color,
                command=self.al_elegir_color,
            )
        ver.add_cascade(label="Luz neon", menu=luz)
        ver.add_separator()
        angular = self.nuevo_menu()
        for indice, (clave, texto) in enumerate(MODOS):
            angular.add_radiobutton(
                label="{0}\tCtrl+{1}".format(texto, indice + 1),
                variable=self.var_modo,
                value=clave,
                command=self.al_elegir_modo,
            )
        ver.add_cascade(label="Modo angular", menu=angular)
        ver.add_separator()
        ver.add_checkbutton(
            label="Ver panel de memoria\tCtrl+M",
            variable=self.var_panel,
            command=self.al_cambiar_panel,
        )
        self.menu.add_cascade(label="Ver", menu=ver)

        calculadora = self.nuevo_menu()
        rapidas = self.nuevo_menu()
        for etiqueta, expresion, atajo in [
            ("Cuadrado del ultimo", "ans^2", "Ctrl+U"),
            ("Raiz del ultimo", "√(ans)", "Ctrl+R"),
            ("Inverso del ultimo", "1/ans", "Ctrl+I"),
            ("Porcentaje del ultimo", "(ans/100)", "Ctrl+P"),
        ]:
            rapidas.add_command(
                label="{0}\t{1}".format(etiqueta, atajo),
                command=lambda e=expresion: self.escribir(e),
            )
        calculadora.add_cascade(label="Operaciones rapidas", menu=rapidas)

        memoria = self.nuevo_menu()
        for etiqueta, comando, atajo in [
            ("Limpiar memoria (MC)", "MC", "Ctrl+Shift+M"),
            ("Traer memoria (MR)", "MR", "Ctrl+Alt+M"),
            ("Sumar a la memoria (M+)", "M+", "Ctrl+Alt+A"),
            ("Restar de la memoria (M-)", "M-", "Ctrl+Alt+R"),
        ]:
            memoria.add_command(
                label="{0}\t{1}".format(etiqueta, atajo),
                command=lambda c=comando: self.operar_memoria(c),
            )
        calculadora.add_cascade(label="Memoria", menu=memoria)
        calculadora.add_separator()
        calculadora.add_command(label="Calcular (Enter)", command=self.calcular)
        self.menu.add_cascade(label="Calculadora", menu=calculadora)

        ayuda = self.nuevo_menu()
        ayuda.add_command(label="Atajos de teclado\tF1", command=self.mostrar_atajos)
        ayuda.add_command(label="Funciones del motor", command=self.mostrar_funciones)
        ayuda.add_command(label="Acerca de...", command=self.mostrar_acerca_de)
        self.menu.add_cascade(label="Ayuda", menu=ayuda)

        self.config(menu=self.menu)

    def crear_atajos(self):
        atajos = {
            "<Control-n>": lambda _e: self.limpiar_todo(),
            "<Control-N>": lambda _e: self.limpiar_todo(),
            "<Control-s>": lambda _e: self.guardar_datos(),
            "<Control-S>": lambda _e: self.guardar_datos(),
            "<Control-e>": lambda _e: self.exportar(),
            "<Control-E>": lambda _e: self.exportar(),
            "<Control-c>": lambda _e: self.copiar_resultado(),
            "<Control-C>": lambda _e: self.copiar_resultado(),
            "<Control-v>": lambda _e: self.pegar_numero(),
            "<Control-V>": lambda _e: self.pegar_numero(),
            "<Control-m>": lambda _e: self.alternar_panel(),
            "<Control-M>": lambda _e: self.alternar_panel(),
            "<Control-u>": lambda _e: self.escribir("ans^2"),
            "<Control-U>": lambda _e: self.escribir("ans^2"),
            "<Control-r>": lambda _e: self.escribir("√(ans)"),
            "<Control-R>": lambda _e: self.escribir("√(ans)"),
            "<Control-i>": lambda _e: self.escribir("1/ans"),
            "<Control-I>": lambda _e: self.escribir("1/ans"),
            "<Control-p>": lambda _e: self.escribir("(ans/100)"),
            "<Control-P>": lambda _e: self.escribir("(ans/100)"),
            "<Control-B>": lambda _e: self.limpiar_historial(),
            "<Control-q>": lambda _e: self.cerrar(),
            "<Control-Q>": lambda _e: self.cerrar(),
            "<F1>": lambda _e: self.mostrar_atajos(),
            "<F2>": lambda _e: self.abrir_ajustes(),
            "<Return>": lambda _e: self.calcular(),
            "<KP_Enter>": lambda _e: self.calcular(),
            "<Escape>": lambda _e: self.limpiar_todo(),
            "<BackSpace>": lambda _e: self.borrar_ultimo(),
        }
        for indice, (clave, _texto) in enumerate(MODOS):
            atajos["<Control-Key-{0}>".format(indice + 1)] = (
                lambda e, m=clave: self.cambiar_modo(m)
            )
        for secuencia, accion in atajos.items():
            self.bind_all(secuencia, accion)

        self.bind("<Button-1>", self.al_clic)
        self.bind("<Double-Button-1>", self.al_doble_clic)
        self.bind("<Configure>", self.al_redimensionar)
        self.bind("<MouseWheel>", self.al_rueda)

    def crear_ui(self):
        marco = ttk.Frame(self, padding=8)
        marco.pack(fill="both", expand=True)

        cabecera = ttk.Frame(marco)
        cabecera.pack(fill="x")
        self.lbl_titulo = ttk.Label(cabecera, text=TITULO, style="Titulo.TLabel")
        self.lbl_titulo.pack(side="left")
        self.lbl_vivo = tk.Label(
            cabecera, text="EN VIVO", bg="#05060f", fg=self.acento,
            font=("Consolas", 10, "bold"),
        )
        self.lbl_vivo.pack(side="right", padx=10)
        self.lbl_reloj = ttk.Label(cabecera, textvariable=self.var_reloj, style="Titulo.TLabel")
        self.lbl_reloj.pack(side="right")

        self.lbl_subtitulo = ttk.Label(
            marco,
            text="Menuus :: F1 ayuda :: F2 ajustes :: doble clic limpia",
            style="Sub.TLabel",
            anchor="center",
        )
        self.lbl_subtitulo.pack(fill="x", pady=(2, 6))

        cuerpo = ttk.Frame(marco)
        cuerpo.pack(fill="both", expand=True)

        self.crear_teclado(cuerpo)
        self.crear_panel(cuerpo)

        pie = ttk.Frame(marco)
        pie.pack(fill="x", pady=(6, 0))
        ttk.Label(
            pie, text="Fue echo por el echicero", style="Pie.TLabel", anchor="center"
        ).pack(fill="x")
        self.lbl_estado = ttk.Label(
            pie, textvariable=self.var_mensaje, style="Sub.TLabel", anchor="center", wraplength=900
        )
        self.lbl_estado.pack(fill="x")

        barra = ttk.Frame(marco, style="Menu.TFrame", padding=4)
        barra.pack(fill="x", pady=(6, 0))
        self.lbl_modo = ttk.Label(barra, textvariable=self.var_modo_texto, style="Estado.TLabel")
        self.lbl_modo.pack(side="left")
        ttk.Label(barra, textvariable=self.var_operacion, style="Sub.TLabel", anchor="center").pack(
            side="left", fill="x", expand=True
        )
        ttk.Label(barra, textvariable=self.var_ultimo, style="Estado.TLabel").pack(side="right")

    def crear_teclado(self, padre):
        grupo = ttk.LabelFrame(padre, text="TECLADO", padding=8)
        grupo.pack(side="left", fill="both", expand=True, padx=(0, 6))
        grupo.columnconfigure(0, weight=1)

        self.var_memoria = tk.StringVar(value="M: 0")
        self.lbl_memoria = ttk.Label(grupo, textvariable=self.var_memoria, style="Memoria.TLabel")
        self.lbl_memoria.grid(row=0, column=0, columnspan=6, sticky="e", pady=(0, 2))

        marco_pantalla = tk.Frame(grupo, bg=self.acento, padx=2, pady=2)
        marco_pantalla.grid(row=1, column=0, columnspan=6, sticky="ew", pady=(0, 6))

        self.var_expresion = tk.StringVar(value="")
        self.txt_expresion = tk.Entry(
            marco_pantalla,
            textvariable=self.var_expresion,
            state="readonly",
            justify="right",
            bg="#0b0f1e",
            fg=self.acento,
            insertbackground=self.acento,
            relief="flat",
            font=("Consolas", 16, "bold"),
        )
        self.txt_expresion.pack(fill="x", ipady=6)

        self.lbl_resultado = ttk.Label(
            marco_pantalla, text="= 0", style="Panel.TLabel", anchor="e"
        )
        self.lbl_resultado.pack(fill="x", pady=(4, 2))

        self.botones = {}
        for posicion, (etiqueta, clase, ayuda) in enumerate(TECLAS):
            estilo = "Numero.TButton" if clase == "numero" else "TButton"
            if etiqueta == "=":
                estilo = "Igual.TButton"
            boton = ttk.Button(
                grupo,
                text=etiqueta,
                style=estilo,
                command=lambda t=etiqueta: self.pulsar(t),
            )
            if etiqueta == "=":
                boton.grid(
                    row=2 + posicion // 6, column=4, columnspan=2, sticky="nsew", padx=2, pady=2
                )
            else:
                boton.grid(
                    row=2 + posicion // 6, column=posicion % 6, sticky="nsew", padx=2, pady=2
                )
            grupo.columnconfigure(posicion % 6, weight=1, minsize=72)
            grupo.rowconfigure(2 + posicion // 6, weight=1, minsize=34)
            self.botones[etiqueta] = boton
            self.señalar(boton, "{0} :: {1}".format(etiqueta, ayuda))

    def crear_panel(self, padre):
        grupo = ttk.LabelFrame(padre, text="MEMORIA E HISTORIAL", padding=8)
        grupo.pack(side="left", fill="both", expand=True)
        grupo.columnconfigure(0, weight=1)
        grupo.rowconfigure(4, weight=1)

        self.cmb_angulo = ttk.Combobox(
            grupo,
            values=[texto for _clave, texto in MODOS],
            state="readonly",
            width=14,
        )
        self.cmb_angulo.current([clave for clave, _ in MODOS].index(self.modo))
        self.cmb_angulo.bind("<<ComboboxSelected>>", self.al_cambiar_modo)
        ttk.Label(grupo, text="Modo angular:").grid(row=0, column=0, sticky="w", pady=3)
        self.cmb_angulo.grid(row=0, column=1, sticky="w", padx=6, pady=3)

        self.ck_panel = ttk.Checkbutton(
            grupo, text="Ver panel", variable=self.var_panel, command=self.al_cambiar_panel
        )
        self.ck_panel.grid(row=1, column=0, columnspan=2, sticky="w", pady=3)

        self.ck_guardar = ttk.Checkbutton(
            grupo,
            text="Guardar historial",
            variable=self.var_guardar,
            command=self.al_cambiar_guardado,
        )
        self.ck_guardar.grid(row=2, column=0, columnspan=2, sticky="w", pady=3)

        ttk.Separator(grupo, orient="horizontal").grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=8
        )

        self.lbl_contador = ttk.Label(grupo, textvariable=self.var_contador, style="Estado.TLabel")
        self.lbl_contador.grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 4))

        self.txt_historial = tk.Text(
            grupo,
            bg="#0b0f1e",
            fg=self.acento,
            insertbackground=self.acento,
            relief="flat",
            font=("Consolas", 10),
            height=14,
            wrap="none",
            state="disabled",
        )
        self.txt_historial.grid(row=5, column=0, columnspan=2, sticky="nsew")

        self.lbl_resumen = ttk.Label(
            grupo, textvariable=self.var_resumen, style="Sub.TLabel", wraplength=380
        )
        self.lbl_resumen.grid(row=6, column=0, columnspan=2, sticky="w", pady=(6, 0))

        self.lbl_mensaje = ttk.Label(
            grupo, textvariable=self.var_mensaje, style="Sub.TLabel", wraplength=380
        )
        self.lbl_mensaje.grid(row=7, column=0, columnspan=2, sticky="w", pady=(4, 6))

        botones = ttk.Frame(grupo)
        botones.grid(row=8, column=0, columnspan=2, sticky="ew")

        self.btn_historial = ttk.Button(botones, text="HISTORIAL", command=self.ver_historial)
        self.btn_historial.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        self.btn_ajustes = ttk.Button(botones, text="AJUSTES", command=self.abrir_ajustes)
        self.btn_ajustes.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        self.btn_copiar = ttk.Button(botones, text="COPIAR", command=self.copiar_resultado)
        self.btn_copiar.grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        self.btn_exportar = ttk.Button(botones, text="EXPORTAR", command=self.exportar)
        self.btn_exportar.grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        self.btn_limpiar = ttk.Button(botones, text="LIMPIAR", command=self.limpiar_historial)
        self.btn_limpiar.grid(row=2, column=0, sticky="ew", padx=2, pady=2)
        self.btn_nuevo = ttk.Button(botones, text="NUEVO", command=self.limpiar_todo)
        self.btn_nuevo.grid(row=2, column=1, sticky="ew", padx=2, pady=2)

        for columna in (0, 1):
            botones.columnconfigure(columna, weight=1)

        for boton, texto in (
            (self.btn_historial, "Abre la ventana con todo el historial"),
            (self.btn_ajustes, "Modo angular, decimales y paneles"),
            (self.btn_copiar, "Copia el resultado al portapapeles"),
            (self.btn_exportar, "Exporta el historial a un archivo"),
            (self.btn_limpiar, "Borra el historial guardado"),
            (self.btn_nuevo, "Reinicia la calculadora"),
        ):
            self.señalar(boton, texto)

    def señalar(self, widget, texto):
        widget.bind("<Enter>", lambda _e: self.notificar(texto))
        widget.bind("<Leave>", lambda _e: None)

    def notificar(self, mensaje):
        self.var_mensaje.set(mensaje)
        self.var_operacion.set(mensaje)

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
        actual = self.var_expresion.get()
        valor = texto.startswith(
            ("sin(", "cos(", "tan(", "ln(", "log(", "exp(", "√(", "abs(", "pi", "e", "(", "1/(", "ans")
        )
        if actual and valor and (
            actual[-1:].isdigit() or actual[-1:] in ".)" or actual.endswith("!")
        ):
            actual += "*"
        for simbolo, ascii_ in (("×", "*"), ("÷", "/"), ("−", "-")):
            texto = texto.replace(simbolo, ascii_)
        self.var_expresion.set(actual + texto)
        self.var_operacion.set("Expresion: {0}".format(bonito(actual + texto)))

    def cerrar_parentesis(self, texto):
        faltan = texto.count("(") - texto.count(")")
        if faltan > 0:
            texto += ")" * faltan
        return texto

    def borrar_ultimo(self):
        texto = self.var_expresion.get()
        self.var_expresion.set(texto[:-1])

    def cambiar_signo(self):
        texto = self.var_expresion.get()
        self.var_expresion.set(texto[1:] if texto.startswith("-") else "-" + texto)

    def limpiar_entrada(self):
        self.var_expresion.set("")
        self.lbl_resultado.configure(text="= 0")
        self.notificar("Entrada limpia")

    def limpiar_todo(self):
        self.limpiar_entrada()
        self.motor.ultimo = 0.0
        self.var_ultimo.set("Ultimo: -")
        self.notificar("Calculadora reiniciada")

    def calcular(self):
        texto = self.cerrar_parentesis(self.var_expresion.get().strip())
        if not texto:
            self.notificar("Escribe algo antes de calcular")
            return

        try:
            valor = self.motor.evaluar(texto)
        except ErrorCalculo as error:
            self.notificar("Error: {0}".format(error))
            messagebox.showwarning("No se pudo calcular", str(error), parent=self)
            return
        except Exception:
            self.notificar("Error: expresion no valida")
            messagebox.showwarning("No se pudo calcular", "La expresion no es valida.", parent=self)
            return

        if valor != valor or valor in (float("inf"), float("-inf")):
            self.notificar("Error: resultado indefinido")
            messagebox.showwarning("No se pudo calcular", "El resultado no existe.", parent=self)
            return

        resultado = self.formatear(valor)
        self.lbl_resultado.configure(text="= {0}".format(resultado))
        self.var_ultimo.set("Ultimo: {0}".format(resultado))
        self.var_expresion.set(resultado)
        self.var_operacion.set("Resultado: {0}".format(resultado))

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

    def operar_memoria(self, comando):
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
        self.var_memoria.set("M: {0}".format(self.formatear(self.memoria)))
        self.var_resumen.set(
            "Memoria: {0} | Calculos: {1}".format(self.formatear(self.memoria), len(self.historial))
        )

    def mostrar_historial(self):
        self.txt_historial.config(state="normal")
        self.txt_historial.delete("1.0", "end")
        if not self.historial:
            self.txt_historial.insert("end", "Todavia no hay calculos.")
        else:
            for indice, item in enumerate(self.historial[:60], start=1):
                self.txt_historial.insert(
                    "end",
                    "{0:02d}. {1} = {2}\n".format(
                        indice, bonito(item["expresion"]), item["resultado"]
                    ),
                )
        self.txt_historial.config(state="disabled")
        self.var_contador.set("Calculos: {0}".format(len(self.historial)))
        self.mostrar_memoria()

    def ver_historial(self):
        self.dialogo_abierto = HistorialDialog(self, self.historial, self.acento)
        self.dialogo_abierto.grab_set()

    def limpiar_historial(self):
        if not self.historial:
            messagebox.showinfo("Aviso", "El historial ya esta vacio.", parent=self)
            return
        if messagebox.askyesno("Borrar historial", "Borrar todos los calculos?", parent=self):
            self.historial = []
            self.mostrar_historial()
            self.guardar_datos()
            self.notificar("Historial borrado")

    def abrir_ajustes(self):
        self.dialogo_abierto = AjustesDialog(
            self, self.modo, self.decimales, self.guardar_historial, self.mostrar_panel, self.acento
        )
        self.dialogo_abierto.grab_set()

    def aplicar_ajustes(self, modo, decimales, guardar, panel):
        self.cambiar_modo(modo)
        self.decimales = decimales
        self.var_decimales.set(str(decimales))
        self.guardar_historial = guardar
        self.mostrar_panel = panel
        self.var_guardar.set(guardar)
        self.var_panel.set(panel)
        self.al_cambiar_panel()
        self.guardar_datos()
        self.notificar("Ajustes guardados")

    def copiar_resultado(self):
        resultado = self.lbl_resultado.cget("text").replace("=", "").strip()
        if resultado in ("", "0"):
            messagebox.showinfo("Aviso", "No hay ningun resultado que copiar.", parent=self)
            return
        self.clipboard_clear()
        self.clipboard_append(resultado)
        self.update()
        self.notificar("Copiado: {0}".format(resultado))

    def pegar_numero(self):
        try:
            texto = self.clipboard_get()
        except tk.TclError:
            messagebox.showinfo("Aviso", "El portapapeles esta vacio.", parent=self)
            return
        limpio = "".join(c for c in texto.strip() if c.isdigit() or c in ".,-")
        if not limpio:
            messagebox.showinfo("Aviso", "El portapapeles no tiene numeros.", parent=self)
            return
        self.escribir(limpio.replace(",", "."))
        self.notificar("Pegado: {0}".format(limpio))

    def exportar(self):
        if not self.historial:
            messagebox.showinfo("Aviso", "No hay calculos para exportar.", parent=self)
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

        messagebox.showinfo("Exportar", "Reporte guardado en:\n{0}".format(ARCHIVO_REPORTE), parent=self)
        self.notificar("Reporte exportado en {0}".format(ARCHIVO_REPORTE))

    def guardar_datos(self):
        datos = {
            "historial": self.historial,
            "memoria": self.memoria,
            "modo": self.modo,
            "acento": self.acento,
            "decimales": self.decimales,
            "guardar_historial": self.guardar_historial,
            "mostrar_panel": self.mostrar_panel,
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
        self.mostrar_panel = bool(datos.get("mostrar_panel", True))
        try:
            self.decimales = int(datos.get("decimales", self.decimales))
        except (TypeError, ValueError):
            self.decimales = 10
        if self.modo not in [clave for clave, _ in MODOS]:
            self.modo = "deg"
        if self.acento not in ACENTOS:
            self.acento = ACENTOS[0]
        self.motor.angulo = self.modo
        self.var_modo.set(self.modo)
        self.var_color.set(self.acento)
        self.var_guardar.set(self.guardar_historial)
        self.var_panel.set(self.mostrar_panel)
        self.var_decimales.set(str(self.decimales))

    def al_elegir_color(self):
        self.aplicar_tema()
        self.notificar("Luz neon cambiada a {0}".format(self.acento))

    def al_elegir_modo(self):
        self.cambiar_modo(self.var_modo.get())

    def cambiar_modo(self, modo):
        if modo not in [clave for clave, _ in MODOS]:
            modo = "deg"
        self.modo = modo
        self.motor.angulo = modo
        self.var_modo.set(modo)
        try:
            self.cmb_angulo.current([clave for clave, _ in MODOS].index(modo))
        except tk.TclError:
            pass
        self.var_modo_texto.set("MODO: {0}".format(self.texto_modo().upper()))
        self.notificar("Modo angular: {0}".format(self.texto_modo().lower()))

    def al_cambiar_modo(self, _evento=None):
        indice = self.cmb_angulo.current()
        if 0 <= indice < len(MODOS):
            self.cambiar_modo(MODOS[indice][0])

    def al_cambiar_panel(self):
        self.mostrar_panel = bool(self.var_panel.get())
        self.var_panel.set(self.mostrar_panel)
        if self.mostrar_panel:
            self.lbl_mensaje.grid()
            self.lbl_resumen.grid()
            self.txt_historial.grid()
        else:
            self.lbl_mensaje.grid_remove()
            self.lbl_resumen.grid_remove()
            self.txt_historial.grid_remove()

    def al_cambiar_guardado(self):
        self.guardar_historial = bool(self.var_guardar.get())
        self.notificar(
            "Historial {0}".format("activado" if self.guardar_historial else "desactivado")
        )

    def alternar_panel(self):
        self.var_panel.set(not self.var_panel.get())
        self.al_cambiar_panel()

    def mostrar_atajos(self):
        dialogo = VentanaDialogo(self, "Atajos de teclado", self.acento, ancho=470, alto=380)
        self.dialogo_abierto = dialogo
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
        tk.Label(
            dialogo.cuerpo, text=texto, bg="#05060f", fg=self.acento, font=("Consolas", 10),
            justify="left",
        ).pack(fill="both", expand=True)
        dialogo.agregar_boton("CERRAR", dialogo.cerrar)
        dialogo.grab_set()

    def mostrar_funciones(self):
        dialogo = VentanaDialogo(self, "Funciones del motor", self.acento, ancho=460, alto=380)
        self.dialogo_abierto = dialogo
        texto = (
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
            "ejemplo: sin(30)+cos(60)*2"
        )
        tk.Label(
            dialogo.cuerpo, text=texto, bg="#05060f", fg=self.acento, font=("Consolas", 10),
            justify="left",
        ).pack(fill="both", expand=True)
        dialogo.agregar_boton("CERRAR", dialogo.cerrar)
        dialogo.grab_set()

    def mostrar_acerca_de(self):
        dialogo = AcercaDeDialog(self, self.acento)
        self.dialogo_abierto = dialogo
        dialogo.grab_set()

    def sigue_vivo(self):
        try:
            return bool(self.winfo_exists())
        except tk.TclError:
            return False

    def tick_reloj(self):
        if not self.sigue_vivo():
            return
        self.var_reloj.set(datetime.now().strftime("%H:%M:%S"))
        self.parpadeo = not self.parpadeo
        self.lbl_vivo.configure(fg=self.acento if self.parpadeo else "#1c2233")
        self.after(1000, self.tick_reloj)

    def guardado_automatico(self):
        if not self.sigue_vivo():
            return
        self.guardar_datos()
        self.notificar("Guardado automatico {0}".format(datetime.now().strftime("%H:%M:%S")))
        self.after(30000, self.guardado_automatico)

    def cambiar_color(self):
        siguiente = ACENTOS[(ACENTOS.index(self.acento) + 1) % len(ACENTOS)]
        self.var_color.set(siguiente)
        self.aplicar_tema()
        self.notificar("Luz neon cambiada a {0}".format(siguiente))

    def al_clic(self, evento):
        if self.dialogo_abierto is None:
            self.var_operacion.set("Clic en {0},{1}".format(evento.x, evento.y))

    def al_doble_clic(self, _evento):
        self.limpiar_entrada()
        self.notificar("Doble clic: entrada limpia")

    def al_rueda(self, evento):
        if self.dialogo_abierto is not None:
            return
        try:
            actual = float(self.lbl_resultado.cget("text").replace("=", "").strip() or 0)
        except ValueError:
            actual = 0.0
        if evento.state & 0x0004:
            nuevo = -actual
            texto = "Ctrl"
        else:
            nuevo = actual * 1.1 if evento.delta > 0 else actual / 1.1
            texto = "Rueda"
        self.lbl_resultado.configure(text="= {0}".format(self.formatear(nuevo)))
        self.notificar("{0}: {1}".format(texto, self.formatear(nuevo)))

    def al_redimensionar(self, evento):
        if evento.widget is self:
            self.lbl_subtitulo.configure(
                text="{0}  ::  {1}x{2}  ::  F1 ayuda  ::  F2 ajustes  ::  doble clic limpia".format(
                    TITULO, evento.width, evento.height
                )
            )

    def cerrar(self):
        self.guardar_datos()
        self.destroy()


def main():
    app = Calculadora()
    app.mainloop()


if __name__ == "__main__":
    main()