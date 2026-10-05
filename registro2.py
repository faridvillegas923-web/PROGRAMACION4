import json
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QTextCursor
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro2_datos.json")


class ConfirmarDialog(QDialog):
    def __init__(self, parent=None, registro=None):
        super().__init__(parent)
        self.registro = registro
        self.setWindowTitle("Confirmar registro")
        self.setModal(True)
        self.setMinimumWidth(360)

        etiqueta = QLabel("Revisa los datos antes de guardar:")
        etiqueta.setFont(QFont("Segoe UI", 10, QFont.Bold))

        self.txt_detalle = QTextEdit()
        self.txt_detalle.setReadOnly(True)
        self.txt_detalle.setPlainText(
            "Nombre: {nombre}\nCédula: {cedula}\nCarrera: {carrera}\nCorreo: {email}\nNota: {nota}".format(
                **registro
            )
        )
        self.txt_detalle.setFixedHeight(140)

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Ok).setText("Guardar")
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(etiqueta)
        layout.addWidget(self.txt_detalle)
        layout.addWidget(botones)


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Registro (registro2)")
        self.resize(760, 620)

        self.registros = []
        self.cargar_datos()

        self.crear_ui()
        self.mostrar_registros()

    def crear_ui(self):
        contenedor = QWidget()
        self.setCentralWidget(contenedor)

        layout = QVBoxLayout(contenedor)

        titulo = QLabel("Registro de Estudiantes y Notas")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        formulario = QFormLayout()
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre completo")
        self.txt_cedula = QLineEdit()
        self.txt_cedula.setPlaceholderText("Cédula / Matrícula")
        self.txt_carrera = QLineEdit()
        self.txt_carrera.setPlaceholderText("Carrera")
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("Correo electrónico")
        self.txt_nota = QLineEdit()
        self.txt_nota.setPlaceholderText("Nota de 0 a 100")
        self.txt_nota.setValidator(QDoubleValidator(0.0, 100.0, 2, self))

        formulario.addRow("Nombre:", self.txt_nombre)
        formulario.addRow("Cédula:", self.txt_cedula)
        formulario.addRow("Carrera:", self.txt_carrera)
        formulario.addRow("Correo:", self.txt_email)
        formulario.addRow("Nota:", self.txt_nota)
        layout.addLayout(formulario)

        self.txt_filtro = QLineEdit()
        self.txt_filtro.setPlaceholderText("Buscar en la lista...")
        self.txt_filtro.textChanged.connect(self.mostrar_registros)
        layout.addWidget(self.txt_filtro)

        self.lbl_registros = QLabel("Registros guardados: 0")
        self.lbl_registros.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(self.lbl_registros)

        self.txt_lista = QTextEdit()
        self.txt_lista.setReadOnly(True)
        layout.addWidget(self.txt_lista)

        self.lbl_estado = QLabel("Fue echo por el echicero")
        self.lbl_estado.setAlignment(Qt.AlignCenter)
        self.lbl_estado.setStyleSheet("color: #555; font-style: italic; padding: 6px;")
        layout.addWidget(self.lbl_estado)

        botones = QHBoxLayout()
        self.btn_registrar = QPushButton("Registrar")
        self.btn_ultimo = QPushButton("Eliminar último")
        self.btn_limpiar = QPushButton("Limpiar formulario")
        self.btn_borrar = QPushButton("Borrar todo")

        self.btn_registrar.clicked.connect(self.registrar)
        self.btn_ultimo.clicked.connect(self.eliminar_ultimo)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        self.btn_borrar.clicked.connect(self.borrar_todo)

        for boton in (self.btn_registrar, self.btn_ultimo, self.btn_limpiar, self.btn_borrar):
            botones.addWidget(boton)

        layout.addLayout(botones)
        self.statusBar().showMessage("Listo")

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
            "carrera": self.txt_carrera.text().strip(),
            "email": self.txt_email.text().strip(),
            "nota": nota,
        }

    def registrar(self):
        registro = self.leer_formulario()
        if registro is None:
            self.lbl_estado.setText("Revisa los campos: la nota debe estar entre 0 y 100")
            QMessageBox.warning(self, "Datos inválidos", "La nota debe ser un número entre 0 y 100.")
            return

        if not registro["nombre"] or not registro["cedula"]:
            self.lbl_estado.setText("Faltan nombre y cédula")
            QMessageBox.warning(self, "Datos incompletos", "El nombre y la cédula son obligatorios.")
            return

        if any(r["cedula"] == registro["cedula"] for r in self.registros):
            self.lbl_estado.setText("Esa cédula ya está registrada")
            QMessageBox.warning(self, "Duplicado", "Ya existe un registro con esa cédula.")
            return

        dialogo = ConfirmarDialog(self, registro)
        if dialogo.exec_() != QDialog.Accepted:
            self.lbl_estado.setText("Registro cancelado")
            return

        self.registros.append(registro)
        self.guardar_datos()
        self.mostrar_registros()
        self.limpiar_formulario()
        self.lbl_estado.setText("Registro guardado correctamente")
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
            self.mostrar_registros()
            self.lbl_estado.setText("Último registro eliminado")

    def limpiar_formulario(self):
        for campo in (
            self.txt_nombre,
            self.txt_cedula,
            self.txt_carrera,
            self.txt_email,
            self.txt_nota,
        ):
            campo.clear()
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
            self.mostrar_registros()
            self.lbl_estado.setText("Todos los registros fueron borrados")

    def mostrar_registros(self, texto_filtro=None):
        if texto_filtro is None:
            texto_filtro = self.txt_filtro.text().strip().lower()

        self.txt_lista.clear()
        visibles = 0
        promedio = 0.0

        for posicion, registro in enumerate(self.registros, start=1):
            linea = (
                "{pos}. {nombre} | {cedula} | {carrera} | {email} | Nota: {nota:.1f}".format(
                    pos=posicion, **registro
                )
            )
            if texto_filtro and texto_filtro not in linea.lower():
                continue

            cursor = self.txt_lista.textCursor()
            cursor.movePosition(QTextCursor.End)
            if visibles > 0:
                cursor.insertBlock()
            cursor.insertText(linea)
            self.txt_lista.setTextCursor(cursor)

            nota = registro["nota"]
            if nota >= 50:
                estado = " APROBADO"
            else:
                estado = " REPROBADO"
            cursor.insertText(estado)

            visibles += 1
            promedio += nota

        if visibles == 0:
            self.txt_lista.setPlainText("No hay registros para mostrar.")
        else:
            promedio /= visibles
            cursor = self.txt_lista.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertBlock()
            cursor.insertText("---- Promedio visible: {0:.2f} ----".format(promedio))

        self.lbl_registros.setText(
            "Registros guardados: {0} | Mostrados: {1}".format(len(self.registros), visibles)
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
