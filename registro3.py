import json
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont
from PyQt5.QtWidgets import (
    QApplication,
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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

ARCHIVO_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro3_datos.json")


class DetalleDialog(QDialog):
    def __init__(self, parent=None, registro=None):
        super().__init__(parent)
        self.registro = registro
        self.setWindowTitle("Detalle del registro")
        self.setModal(True)
        self.setMinimumWidth(380)

        encabezado = QLabel(
            "{nombre}  ({cedula})".format(**registro) if registro else "Sin registro"
        )
        encabezado.setFont(QFont("Segoe UI", 12, QFont.Bold))
        encabezado.setAlignment(Qt.AlignCenter)

        self.txt_detalle = QTextEdit()
        self.txt_detalle.setReadOnly(True)
        self.txt_detalle.setFixedHeight(180)
        if registro:
            self.txt_detalle.setPlainText(
                "Carrera: {carrera}\n"
                "Correo: {email}\n"
                "Materia: {materia}\n"
                "Nota: {nota}\n"
                "Resultado: {resultado}\n"
                "Posición en la lista: {posicion}".format(
                    resultado="APROBADO" if registro["nota"] >= 50 else "REPROBADO", **registro
                )
            )

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(self.reject)
        botones.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(encabezado)
        layout.addWidget(self.txt_detalle)
        layout.addWidget(botones)


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Registro (registro3)")
        self.resize(880, 660)

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
        self.crear_panel_resumen(fila_panel)

        self.txt_filtro = QLineEdit()
        self.txt_filtro.setPlaceholderText("Buscar por nombre, cédula, carrera o materia...")
        self.txt_filtro.textChanged.connect(self.mostrar_registros)
        raiz.addWidget(self.txt_filtro)

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
        panel.setStyleSheet("QWidget { border: 1px solid #ccc; border-radius: 4px; }")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)

        etiqueta = QLabel("Datos del estudiante")
        etiqueta.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(etiqueta)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre completo")
        self.txt_cedula = QLineEdit()
        self.txt_cedula.setPlaceholderText("Cédula / Matrícula")
        self.txt_carrera = QLineEdit()
        self.txt_carrera.setPlaceholderText("Carrera")
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("Correo electrónico")
        self.txt_materia = QLineEdit()
        self.txt_materia.setPlaceholderText("Materia")
        self.txt_nota = QLineEdit()
        self.txt_nota.setPlaceholderText("Nota de 0 a 100")
        self.txt_nota.setValidator(QDoubleValidator(0.0, 100.0, 2, self))

        formulario = QFormLayout()
        formulario.addRow("Nombre:", self.txt_nombre)
        formulario.addRow("Cédula:", self.txt_cedula)
        formulario.addRow("Carrera:", self.txt_carrera)
        formulario.addRow("Correo:", self.txt_email)
        formulario.addRow("Materia:", self.txt_materia)
        formulario.addRow("Nota:", self.txt_nota)
        layout.addLayout(formulario)

        self.btn_registrar = QPushButton("Registrar")
        self.btn_limpiar = QPushButton("Limpiar formulario")
        self.btn_ultimo = QPushButton("Eliminar último")
        self.btn_detalle = QPushButton("Ver detalle")
        self.btn_borrar = QPushButton("Borrar todo")

        self.btn_registrar.clicked.connect(self.registrar)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        self.btn_ultimo.clicked.connect(self.eliminar_ultimo)
        self.btn_detalle.clicked.connect(self.ver_detalle)
        self.btn_borrar.clicked.connect(self.borrar_todo)

        botones = QHBoxLayout()
        botones.addWidget(self.btn_registrar)
        botones.addWidget(self.btn_limpiar)
        layout.addLayout(botones)

        botones_extra = QHBoxLayout()
        botones_extra.addWidget(self.btn_detalle)
        botones_extra.addWidget(self.btn_ultimo)
        botones_extra.addWidget(self.btn_borrar)
        layout.addLayout(botones_extra)

        self.lbl_estado = QLabel("Esperando datos...")
        self.lbl_estado.setWordWrap(True)
        layout.addWidget(self.lbl_estado)

        layout_padre.addWidget(panel, 3)

    def crear_panel_resumen(self, layout_padre):
        panel = QWidget()
        panel.setStyleSheet("QWidget { border: 1px solid #ccc; border-radius: 4px; }")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)

        etiqueta = QLabel("Resumen")
        etiqueta.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(etiqueta)

        self.lbl_total = QLabel("0")
        self.lbl_aprobados = QLabel("0")
        self.lbl_reprobados = QLabel("0")
        self.lbl_promedio = QLabel("0.00")
        self.lbl_mejor = QLabel("0.00")
        self.lbl_menor = QLabel("0.00")

        cuadricula = QGridLayout()
        titulos = ["Total", "Aprobados", "Reprobados", "Promedio", "Nota más alta", "Nota más baja"]
        valores = [
            self.lbl_total,
            self.lbl_aprobados,
            self.lbl_reprobados,
            self.lbl_promedio,
            self.lbl_mejor,
            self.lbl_menor,
        ]
        for indice, (titulo_resumen, valor) in enumerate(zip(titulos, valores)):
            valor.setAlignment(Qt.AlignCenter)
            valor.setFont(QFont("Segoe UI", 13, QFont.Bold))
            cuadricula.addWidget(QLabel(titulo_resumen), indice // 2, (indice % 2) * 2)
            cuadricula.addWidget(valor, indice // 2, (indice % 2) * 2 + 1)
        cuadricula.setVerticalSpacing(8)
        layout.addLayout(cuadricula)

        acciones = QGridLayout()
        self.btn_subir_nota = QPushButton("Subir nota")
        self.btn_bajar_nota = QPushButton("Bajar nota")
        self.btn_ordenar = QPushButton("Ordenar")
        self.btn_exportar = QPushButton("Exportar")
        self.btn_subir_nota.clicked.connect(lambda: self.sumar_nota(1.0))
        self.btn_bajar_nota.clicked.connect(lambda: self.sumar_nota(-1.0))
        self.btn_ordenar.clicked.connect(self.ordenar)
        self.btn_exportar.clicked.connect(self.exportar)
        acciones.addWidget(self.btn_subir_nota, 0, 0)
        acciones.addWidget(self.btn_bajar_nota, 0, 1)
        acciones.addWidget(self.btn_ordenar, 1, 0)
        acciones.addWidget(self.btn_exportar, 1, 1)
        layout.addLayout(acciones)

        layout.addStretch()
        layout_padre.addWidget(panel, 2)

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
            "materia": self.txt_materia.text().strip(),
            "nota": nota,
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
        self.lbl_estado.setText("Registro guardado correctamente.")
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

        registro = dict(registro, posicion=self.registros.index(registro) + 1)
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
            self.txt_carrera,
            self.txt_email,
            self.txt_materia,
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
            self.actualizar_resumen()
            self.mostrar_registros()
            self.lbl_estado.setText("Todos los registros fueron borrados.")

    def sumar_nota(self, cantidad):
        registro = self.registro_seleccionado()
        if registro is None:
            QMessageBox.information(self, "Aviso", "No hay ningún registro seleccionado.")
            return

        nueva = min(100.0, max(0.0, registro["nota"] + cantidad))
        registro["nota"] = nueva
        self.guardar_datos()
        self.actualizar_resumen()
        self.mostrar_registros()
        self.lbl_estado.setText("Nota de {0} ahora es {1:.1f}".format(registro["nombre"], nueva))

    def ordenar(self):
        if not self.registros:
            QMessageBox.information(self, "Aviso", "No hay registros para ordenar.")
            return

        self.registros.sort(key=lambda r: r["nombre"].lower())
        self.guardar_datos()
        self.mostrar_registros()
        self.lbl_estado.setText("Lista ordenada por nombre.")

    def exportar(self):
        if not self.registros:
            QMessageBox.information(self, "Aviso", "No hay registros para exportar.")
            return

        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro3_reporte.txt")
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write("REPORTE DE ESTUDIANTES - Fue echo por el echicero\n")
            archivo.write("=" * 55 + "\n")
            for posicion, registro in enumerate(self.registros, start=1):
                archivo.write(
                    "{0}. {1} ({2}) | {3} | {4} | Nota: {5:.1f}\n".format(
                        posicion,
                        registro["nombre"],
                        registro["cedula"],
                        registro["carrera"],
                        registro["materia"],
                        registro["nota"],
                    )
                )
            notas = [r["nota"] for r in self.registros]
            archivo.write("-" * 55 + "\n")
            archivo.write("Total: {0} | Promedio: {1:.2f}\n".format(
                len(notas), sum(notas) / len(notas)
            ))

        QMessageBox.information(self, "Exportar", "Reporte guardado en:\n{0}".format(ruta))
        self.lbl_estado.setText("Reporte exportado.")

    def actualizar_resumen(self):
        notas = [r["nota"] for r in self.registros]
        self.lbl_total.setText(str(len(notas)))
        self.lbl_aprobados.setText(str(sum(1 for n in notas if n >= 50)))
        self.lbl_reprobados.setText(str(sum(1 for n in notas if n < 50)))
        self.lbl_promedio.setText("{0:.2f}".format(sum(notas) / len(notas)) if notas else "0.00")
        self.lbl_mejor.setText("{0:.1f}".format(max(notas)) if notas else "0.00")
        self.lbl_menor.setText("{0:.1f}".format(min(notas)) if notas else "0.00")

    def mostrar_registros(self, texto_filtro=None):
        if texto_filtro is None:
            texto_filtro = self.txt_filtro.text().strip().lower()

        self.txt_lista.clear()
        self.visibles = []
        lineas = []

        for posicion, registro in enumerate(self.registros, start=1):
            linea = (
                "{pos}. {nombre} | {cedula} | {carrera} | {materia} | Nota: {nota:.1f} {estado}"
            ).format(
                pos=posicion,
                estado="APROBADO" if registro["nota"] >= 50 else "REPROBADO",
                **registro
            )
            if texto_filtro and texto_filtro not in linea.lower():
                continue
            lineas.append(linea)
            self.visibles.append((posicion, registro))

        if not lineas:
            self.txt_lista.setPlainText("No hay registros para mostrar.")
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
