import json
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGridLayout,
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

ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro4_datos.json")

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


class DetalleDialog(QDialog):
    def __init__(self, parent=None, registro=None):
        super().__init__(parent)
        self.registro = registro
        self.setWindowTitle("Detalle del registro")
        self.setModal(True)
        self.setMinimumWidth(420)

        encabezado = QLabel("Ficha del estudiante")
        encabezado.setFont(QFont("Segoe UI", 13, QFont.Bold))
        encabezado.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QDialog { background: #f7f7f7; }")

        formulario = QFormLayout()
        self.txt_detalle = QTextEdit()
        self.txt_detalle.setReadOnly(True)
        self.txt_detalle.setFixedHeight(120)

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
            self.txt_detalle.setPlainText(
                "Nombre: {nombre}\nCédula: {cedula}\nCorreo: {email}\n"
                "Materia: {materia} | Nota: {nota}".format(**registro)
            )
            indice = self.cmb_carrera.findText(registro["carrera"])
            if indice >= 0:
                self.cmb_carrera.setCurrentIndex(indice)
            (self.rb_activo if registro["activo"] else self.rb_inactivo).setChecked(True)
            self.ck_becado.setChecked(registro["becado"])
            self.ck_repetidor.setChecked(registro["repetidor"])

        formulario.addRow("Datos:", self.txt_detalle)
        formulario.addRow("Carrera:", self.cmb_carrera)
        formulario.addRow("Estado:", estado)
        formulario.addRow("Marcas:", marcas)

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(self.reject)
        botones.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(encabezado)
        layout.addLayout(formulario)
        layout.addWidget(botones)


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Registro (registro4)")
        self.resize(940, 700)

        self.registros = []
        self.visibles = []
        self.cargar_datos()

        self.crear_ui()
        self.actualizar_resumen()
        self.mostrar_registros()

    def crear_ui(self):
        contenedor = QWidget()
        self.setCentralWidget(contenedor)

        raiz = QVBoxLayout(contenedor)

        titulo = QLabel("Registro de Estudiantes y Notas")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        raiz.addWidget(titulo)

        panel = QWidget()
        raiz.addWidget(panel)
        fila_panel = QHBoxLayout(panel)
        self.crear_panel_datos(fila_panel)
        self.crear_panel_filtros(fila_panel)

        raiz.addLayout(self.crear_barra_busqueda())

        self.lbl_contador = QLabel("Registros guardados: 0")
        self.lbl_contador.setFont(QFont("Segoe UI", 10, QFont.Bold))
        raiz.addWidget(self.lbl_contador)

        self.txt_lista = QTextEdit()
        self.txt_lista.setReadOnly(True)
        raiz.addWidget(self.txt_lista)

        pie = QLabel("Fue echo por el echicero")
        pie.setAlignment(Qt.AlignCenter)
        pie.setStyleSheet("color: #555; font-style: italic; padding: 6px;")
        raiz.addWidget(pie)

        self.statusBar().showMessage("Listo")

    def crear_panel_datos(self, layout_padre):
        panel = QWidget()
        panel.setObjectName("datos")
        panel.setStyleSheet("QWidget#datos { border: 1px solid #ccc; border-radius: 4px; }")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)

        etiqueta = QLabel("Datos del estudiante")
        etiqueta.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(etiqueta)

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

        self.lbl_estado = QLabel("Esperando datos...")
        self.lbl_estado.setWordWrap(True)
        layout.addWidget(self.lbl_estado)

        self.btn_registrar = QPushButton("Registrar")
        self.btn_limpiar = QPushButton("Limpiar formulario")
        self.btn_ultimo = QPushButton("Eliminar último")
        self.btn_detalle = QPushButton("Ver detalle")
        self.btn_borrar = QPushButton("Borrar todo")
        self.btn_ordenar = QPushButton("Ordenar")
        self.btn_exportar = QPushButton("Exportar")

        self.btn_registrar.clicked.connect(self.registrar)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        self.btn_ultimo.clicked.connect(self.eliminar_ultimo)
        self.btn_detalle.clicked.connect(self.ver_detalle)
        self.btn_borrar.clicked.connect(self.borrar_todo)
        self.btn_ordenar.clicked.connect(self.ordenar)
        self.btn_exportar.clicked.connect(self.exportar)

        botones = QHBoxLayout()
        botones.addWidget(self.btn_registrar)
        botones.addWidget(self.btn_limpiar)
        layout.addLayout(botones)

        botones_extra = QHBoxLayout()
        for boton in (self.btn_detalle, self.btn_ultimo, self.btn_ordenar):
            botones_extra.addWidget(boton)
        botones_extra.addWidget(self.btn_exportar)
        botones_extra.addWidget(self.btn_borrar)
        layout.addLayout(botones_extra)

        layout_padre.addWidget(panel, 3)

    def crear_panel_filtros(self, layout_padre):
        panel = QWidget()
        panel.setObjectName("datos")
        panel.setStyleSheet("QWidget#datos { border: 1px solid #ccc; border-radius: 4px; }")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)

        etiqueta = QLabel("Filtros y resumen")
        etiqueta.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(etiqueta)

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
            casilla.stateChanged.connect(lambda _estado: self.mostrar_registros())
            layout.addWidget(casilla)

        etiqueta_orden = QLabel("Ordenar por:")
        etiqueta_orden.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(etiqueta_orden)

        self.rb_por_nombre = QRadioButton("Nombre")
        self.rb_por_nota = QRadioButton("Nota (mayor a menor)")
        self.rb_por_carrera = QRadioButton("Carrera")
        self.rb_por_nombre.setChecked(True)
        for boton in (self.rb_por_nombre, self.rb_por_nota, self.rb_por_carrera):
            boton.toggled.connect(lambda _marcado: self.ordenar())
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
        for indice, (titulo_resumen, valor) in enumerate(zip(titulos, valores)):
            valor.setAlignment(Qt.AlignCenter)
            valor.setFont(QFont("Segoe UI", 13, QFont.Bold))
            cuadricula.addWidget(QLabel(titulo_resumen), indice // 2, (indice % 2) * 2)
            cuadricula.addWidget(valor, indice // 2, (indice % 2) * 2 + 1)
        cuadricula.setVerticalSpacing(8)
        layout.addLayout(cuadricula)

        layout.addStretch()
        layout_padre.addWidget(panel, 2)

    def crear_barra_busqueda(self):
        barra = QHBoxLayout()

        self.cmb_campo = QComboBox()
        self.cmb_campo.addItems(["Nombre", "Cédula", "Carrera", "Correo", "Materia", "Nota"])
        self.cmb_campo.setFixedWidth(120)

        self.txt_filtro = QLineEdit()
        self.txt_filtro.setPlaceholderText("Buscar...")
        self.txt_filtro.textChanged.connect(lambda _texto: self.mostrar_registros())

        self.cmb_nota_min = QComboBox()
        self.cmb_nota_min.addItems(["Todas"] + [str(n) for n in range(0, 101, 10)])

        self.cmb_campo.currentIndexChanged.connect(lambda _indice: self.mostrar_registros())
        self.cmb_nota_min.currentIndexChanged.connect(lambda _indice: self.mostrar_registros())

        barra.addWidget(QLabel("Campo:"))
        barra.addWidget(self.cmb_campo)
        barra.addWidget(self.txt_filtro, 1)
        barra.addWidget(QLabel("Nota mínima:"))
        barra.addWidget(self.cmb_nota_min)
        return barra

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
            self.lbl_estado.setText("La nota debe ser un número entre 0 y 100.")
            QMessageBox.warning(self, "Datos inválidos", "La nota debe estar entre 0 y 100.")
            return

        if not registro["nombre"] or not registro["cedula"] or not registro["materia"]:
            self.lbl_estado.setText("Faltan nombre, cédula o materia.")
            QMessageBox.warning(
                self, "Datos incompletos", "Nombre, cédula y materia son obligatorios."
            )
            return

        if any(r["cedula"] == registro["cedula"] for r in self.registros):
            self.lbl_estado.setText("Esa cédula ya está registrada.")
            QMessageBox.warning(self, "Duplicado", "Ya existe un registro con esa cédula.")
            return

        self.registros.append(registro)
        self.guardar_datos()
        self.actualizar_resumen()
        self.mostrar_registros()
        self.limpiar_formulario()
        marcas = []
        if registro["becado"]:
            marcas.append("becado")
        if registro["repetidor"]:
            marcas.append("repetidor")
        self.lbl_estado.setText(
            "Registro guardado. {0}".format(
                "Marcas: " + ", ".join(marcas) if marcas else "Sin marcas."
            )
        )
        self.statusBar().showMessage("Registro guardado", 3000)

    def eliminar_ultimo(self):
        if not self.registros:
            QMessageBox.information(self, "Aviso", "No hay registros para eliminar.")
            return

        respuesta = QMessageBox.question(
            self, "Eliminar", "¿Eliminar el último registro de la lista?"
        )
        if respuesta == QMessageBox.Yes:
            self.registros.pop()
            self.guardar_datos()
            self.actualizar_resumen()
            self.mostrar_registros()
            self.lbl_estado.setText("Último registro eliminado.")

    def ver_detalle(self):
        registro = self.registro_seleccionado()
        if registro is None:
            QMessageBox.information(self, "Aviso", "No hay ningún registro seleccionado.")
            return

        dialogo = DetalleDialog(self, registro)
        dialogo.exec_()

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
            self.lbl_estado.setText("Todos los registros fueron borrados.")

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

        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro4_reporte.txt")
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write("REPORTE DE ESTUDIANTES - Fue echo por el echicero\n")
            archivo.write("=" * 60 + "\n")
            for posicion, registro in enumerate(self.registros, start=1):
                marcas = []
                if registro["becado"]:
                    marcas.append("becado")
                if registro["repetidor"]:
                    marcas.append("repetidor")
                estado = "activo" if registro["activo"] else "inactivo"
                archivo.write(
                    "{0}. {1} ({2}) | {3} | {4} | Nota: {5:.1f} | {6} | {7}\n".format(
                        posicion,
                        registro["nombre"],
                        registro["cedula"],
                        registro["carrera"],
                        registro["materia"],
                        registro["nota"],
                        estado,
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
        self.lbl_estado.setText("Reporte exportado.")

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
            estado = "A" if registro["activo"] else "I"
            linea = (
                "{pos}. {nombre} | {cedula} | {carrera} | {materia} | Nota: {nota:.1f} "
                "{resultado} [{estado}]{marcas}"
            ).format(
                pos=posicion,
                resultado="APROBADO" if registro["nota"] >= 50 else "REPROBADO",
                estado=estado,
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

    def cerrarEvento(self, evento):
        self.guardar_datos()
        evento.accept()


def main():
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
