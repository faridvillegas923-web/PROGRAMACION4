import json
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro1_datos.json")


class EstudianteDialog(QDialog):
    def __init__(self, parent=None, estudiante=None):
        super().__init__(parent)
        self.estudiante = estudiante
        self.setWindowTitle("Editar estudiante" if estudiante else "Registrar estudiante")
        self.setModal(True)
        self.setMinimumWidth(380)

        self.txt_nombre = QLineEdit()
        self.txt_cedula = QLineEdit()
        self.txt_email = QLineEdit()
        self.cmb_carrera = QComboBox()
        self.cmb_carrera.addItems(
            [
                "Ingeniería en Sistemas",
                "Ingeniería Electrónica",
                "Contaduría",
                "Administración",
                "Psicología",
                "Derecho",
                "Medicina",
                "Arquitectura",
            ]
        )

        formulario = QFormLayout()
        formulario.addRow("Nombre completo:", self.txt_nombre)
        formulario.addRow("Cédula / Matrícula:", self.txt_cedula)
        formulario.addRow("Carrera:", self.cmb_carrera)
        formulario.addRow("Correo:", self.txt_email)

        botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(formulario)
        layout.addWidget(botones)

        if estudiante:
            self.txt_nombre.setText(estudiante.get("nombre", ""))
            self.txt_cedula.setText(estudiante.get("cedula", ""))
            self.txt_email.setText(estudiante.get("email", ""))
            indice = self.cmb_carrera.findText(estudiante.get("carrera", ""))
            if indice >= 0:
                self.cmb_carrera.setCurrentIndex(indice)

    def datos(self):
        return {
            "nombre": self.txt_nombre.text().strip(),
            "cedula": self.txt_cedula.text().strip(),
            "carrera": self.cmb_carrera.currentText(),
            "email": self.txt_email.text().strip(),
        }


class NotaDialog(QDialog):
    def __init__(self, parent=None, estudiante=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar nota")
        self.setModal(True)
        self.setMinimumWidth(340)

        nombres = estudiante if estudiante else []

        self.cmb_estudiante = QComboBox()
        for est in nombres:
            self.cmb_estudiante.addItem(f"{est['nombre']} ({est['cedula']})", est["cedula"])

        self.txt_materia = QLineEdit()
        self.txt_materia.setPlaceholderText("Ej: Estructuras de Datos")

        self.spin_nota = QDoubleSpinBox()
        self.spin_nota.setRange(0.0, 100.0)
        self.spin_nota.setDecimals(1)
        self.spin_nota.setSingleStep(0.5)
        self.spin_nota.setValue(70.0)

        formulario = QFormLayout()
        formulario.addRow("Estudiante:", self.cmb_estudiante)
        formulario.addRow("Materia:", self.txt_materia)
        formulario.addRow("Nota (0 - 100):", self.spin_nota)

        botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(formulario)
        layout.addWidget(botones)

    def datos(self):
        return {
            "cedula": self.cmb_estudiante.currentData(),
            "materia": self.txt_materia.text().strip(),
            "nota": self.spin_nota.value(),
        }


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Registro de Estudiantes y Notas")
        self.resize(900, 600)

        self.estudiantes = []
        self.notas = []
        self.cargar_datos()

        self.crear_ui()
        self.actualizar_tablas()

    def crear_ui(self):
        contenedor = QWidget()
        self.setCentralWidget(contenedor)

        layout_principal = QVBoxLayout(contenedor)

        titulo = QLabel("Registro de Estudiantes y Notas")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(titulo)

        self.tabs = QTabWidget()
        layout_principal.addWidget(self.tabs)

        self.tabs.addTab(self.crear_pestania_estudiantes(), "Estudiantes")
        self.tabs.addTab(self.crear_pestania_notas(), "Notas")
        self.tabs.addTab(self.crear_pestania_promedios(), "Promedios")

        pie = QLabel("Fue echo por el echicero")
        pie.setAlignment(Qt.AlignCenter)
        pie.setStyleSheet("color: #555; font-style: italic; padding: 6px;")
        layout_principal.addWidget(pie)

    def crear_pestania_estudiantes(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)

        self.tabla_estudiantes = QTableWidget(0, 6)
        self.tabla_estudiantes.setHorizontalHeaderLabels(
            ["Cédula", "Nombre", "Carrera", "Correo", "Notas", "Promedio"]
        )
        self.tabla_estudiantes.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_estudiantes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_estudiantes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_estudiantes)

        botones = QHBoxLayout()
        self.btn_agregar = QPushButton("Registrar estudiante")
        self.btn_editar = QPushButton("Editar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_limpiar = QPushButton("Limpiar todo")

        self.btn_agregar.clicked.connect(self.registrar_estudiante)
        self.btn_editar.clicked.connect(self.editar_estudiante)
        self.btn_eliminar.clicked.connect(self.eliminar_estudiante)
        self.btn_limpiar.clicked.connect(self.limpiar_datos)

        for boton in (self.btn_agregar, self.btn_editar, self.btn_eliminar, self.btn_limpiar):
            botones.addWidget(boton)

        layout.addLayout(botones)
        return pagina

    def crear_pestania_notas(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)

        self.tabla_notas = QTableWidget(0, 4)
        self.tabla_notas.setHorizontalHeaderLabels(["Estudiante", "Materia", "Nota", "Resultado"])
        self.tabla_notas.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_notas.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_notas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_notas)

        botones = QHBoxLayout()
        self.btn_agregar_nota = QPushButton("Registrar nota")
        self.btn_eliminar_nota = QPushButton("Eliminar nota")

        self.btn_agregar_nota.clicked.connect(self.registrar_nota)
        self.btn_eliminar_nota.clicked.connect(self.eliminar_nota)

        botones.addWidget(self.btn_agregar_nota)
        botones.addWidget(self.btn_eliminar_nota)
        layout.addLayout(botones)
        return pagina

    def crear_pestania_promedios(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)

        self.tabla_promedios = QTableWidget(0, 4)
        self.tabla_promedios.setHorizontalHeaderLabels(
            ["Cédula", "Estudiante", "Materias", "Promedio"]
        )
        self.tabla_promedios.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_promedios.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_promedios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tabla_promedios)
        return pagina

    def guardar_datos(self):
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
            json.dump({"estudiantes": self.estudiantes, "notas": self.notas}, archivo, indent=2)

    def cargar_datos(self):
        if not os.path.exists(ARCHIVO_DATOS):
            return
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
            self.estudiantes = datos.get("estudiantes", [])
            self.notas = datos.get("notas", [])
        except (json.JSONDecodeError, OSError):
            self.estudiantes = []
            self.notas = []

    def actualizar_tablas(self):
        self.tabla_estudiantes.setRowCount(0)
        for est in self.estudiantes:
            notas = [n["nota"] for n in self.notas if n["cedula"] == est["cedula"]]
            promedio = sum(notas) / len(notas) if notas else 0.0
            fila = self.tabla_estudiantes.rowCount()
            self.tabla_estudiantes.insertRow(fila)
            valores = [
                est["cedula"],
                est["nombre"],
                est["carrera"],
                est["email"],
                str(len(notas)),
                f"{promedio:.2f}",
            ]
            for columna, valor in enumerate(valores):
                self.tabla_estudiantes.setItem(fila, columna, QTableWidgetItem(valor))

        self.tabla_notas.setRowCount(0)
        for nota in self.notas:
            nombre = next(
                (e["nombre"] for e in self.estudiantes if e["cedula"] == nota["cedula"]),
                nota["cedula"],
            )
            fila = self.tabla_notas.rowCount()
            self.tabla_notas.insertRow(fila)
            estado = "Aprobado" if nota["nota"] >= 50 else "Reprobado"
            valores = [nombre, nota["materia"], f"{nota['nota']:.1f}", estado]
            for columna, valor in enumerate(valores):
                self.tabla_notas.setItem(fila, columna, QTableWidgetItem(valor))

        self.tabla_promedios.setRowCount(0)
        for est in self.estudiantes:
            notas = [n["nota"] for n in self.notas if n["cedula"] == est["cedula"]]
            promedio = sum(notas) / len(notas) if notas else 0.0
            fila = self.tabla_promedios.rowCount()
            self.tabla_promedios.insertRow(fila)
            valores = [
                est["cedula"],
                est["nombre"],
                str(len(notas)),
                f"{promedio:.2f}",
            ]
            for columna, valor in enumerate(valores):
                self.tabla_promedios.setItem(fila, columna, QTableWidgetItem(valor))

    def registrar_estudiante(self):
        dialogo = EstudianteDialog(self)
        if dialogo.exec_() != QDialog.Accepted:
            return

        datos = dialogo.datos()
        if not datos["nombre"] or not datos["cedula"]:
            QMessageBox.warning(self, "Datos incompletos", "El nombre y la cédula son obligatorios.")
            return

        if any(e["cedula"] == datos["cedula"] for e in self.estudiantes):
            QMessageBox.warning(self, "Duplicado", "Ya existe un estudiante con esa cédula.")
            return

        self.estudiantes.append(datos)
        self.guardar_datos()
        self.actualizar_tablas()
        QMessageBox.information(self, "Registro", "Estudiante registrado correctamente.")

    def editar_estudiante(self):
        fila = self.tabla_estudiantes.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Aviso", "Selecciona un estudiante de la tabla.")
            return

        dialogo = EstudianteDialog(self, self.estudiantes[fila])
        if dialogo.exec_() != QDialog.Accepted:
            return

        datos = dialogo.datos()
        if not datos["nombre"] or not datos["cedula"]:
            QMessageBox.warning(self, "Datos incompletos", "El nombre y la cédula son obligatorios.")
            return

        self.estudiantes[fila] = datos
        self.guardar_datos()
        self.actualizar_tablas()

    def eliminar_estudiante(self):
        fila = self.tabla_estudiantes.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Aviso", "Selecciona un estudiante de la tabla.")
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar",
            "¿Seguro que deseas eliminar al estudiante seleccionado?",
        )
        if respuesta == QMessageBox.Yes:
            cedula = self.estudiantes[fila]["cedula"]
            self.estudiantes.pop(fila)
            self.notas = [n for n in self.notas if n["cedula"] != cedula]
            self.guardar_datos()
            self.actualizar_tablas()

    def registrar_nota(self):
        if not self.estudiantes:
            QMessageBox.information(self, "Aviso", "Primero registra al menos un estudiante.")
            return

        dialogo = NotaDialog(self, self.estudiantes)
        if dialogo.exec_() != QDialog.Accepted:
            return

        datos = dialogo.datos()
        if not datos["materia"]:
            QMessageBox.warning(self, "Datos incompletos", "La materia es obligatoria.")
            return

        self.notas.append(datos)
        self.guardar_datos()
        self.actualizar_tablas()
        self.tabs.setCurrentIndex(1)

    def eliminar_nota(self):
        fila = self.tabla_notas.currentRow()
        if fila < 0:
            QMessageBox.information(self, "Aviso", "Selecciona una nota de la tabla.")
            return

        self.notas.pop(fila)
        self.guardar_datos()
        self.actualizar_tablas()

    def limpiar_datos(self):
        respuesta = QMessageBox.question(
            self,
            "Limpiar todo",
            "¿Deseas borrar todos los estudiantes y las notas?",
        )
        if respuesta == QMessageBox.Yes:
            self.estudiantes = []
            self.notas = []
            self.guardar_datos()
            self.actualizar_tablas()

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
