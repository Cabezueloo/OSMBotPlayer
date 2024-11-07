from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import sys
import subprocess  # Para ejecutar el juego como otro proceso


class Menu(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parametros del BOT")
        self.resize(400, 400)

        self.nombreEquipo = QLineEdit()
        self.nombreEquipo.setFont(QFont("Arial", 10))

        self.millonesCompraVenta = QLineEdit()
        self.millonesCompraVenta.setValidator(QIntValidator())
        self.millonesCompraVenta.setFont(QFont("Arial", 10))

        # creating the check-box
        self.checkbox_video_monedas = QCheckBox('Ver videos automaticamente para conseguir monedas', self)
        self.checkbox_video_monedas.setChecked(True)

        self.checkbox_compra_venta = QCheckBox('Control de compra-venta de jugadoes', self)
        self.checkbox_compra_venta.setChecked(True)

        self.checkbox_control_jugadores = QCheckBox('Control de entrenar jugadores', self)
        self.checkbox_control_jugadores.setChecked(True)

        self.layoutChecksBoxs = QHBoxLayout()
        self.layoutChecksBoxs.addWidget(self.checkbox_video_monedas)
        self.layoutChecksBoxs.addWidget(self.checkbox_compra_venta)
        self.layoutChecksBoxs.addWidget(self.checkbox_control_jugadores)

       

        btn_start = QPushButton("Start")
        btn_start.clicked.connect(self.btn_clicked)

        flo = QFormLayout()
        flo.addRow("Nombre del equipo a controlar", self.nombreEquipo)
        flo.addRow("Millones que tienes que tener para buscar jugadores y comprar-vender", self.millonesCompraVenta)
        flo.addRow(self.layoutChecksBoxs)
        flo.addRow(btn_start)

        self.setLayout(flo)

    def btn_clicked(self):

        nombreEquipo: str = self.nombreEquipo.text()
        millonesMinimos: int = int(self.millonesCompraVenta.text())
        controlVideoMonedas: bool = self.checkbox_video_monedas.isChecked()
        controlCompraVenta: bool = self.checkbox_compra_venta.isChecked()
        controlEntrenamientoJugadores: bool = self.checkbox_control_jugadores.isChecked()

        print(nombreEquipo)
        print(millonesMinimos)
        print("Control Video Monedas-> ", controlVideoMonedas)
        print("Control Compra-Venta-> ", controlCompraVenta)
        print("Control Entrenamiento Jugadores-> ", controlEntrenamientoJugadores)

       
        # Ejecutar el bot con los parámetros introducidos
        self.setEnabled(False)
        self.setVisible(False)

        

        subprocess.run([sys.executable, "main.py",
                        nombreEquipo,
                        str(millonesMinimos),
                        str(controlVideoMonedas),
                        str(controlCompraVenta),
                        str(controlEntrenamientoJugadores)],
                    stdout=sys.stdout,
                    stderr=sys.stderr)
        

        # Volver a habilitar el menú una vez termine el bot
        self.setEnabled(True)
        self.setVisible(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Menu()
    win.show()
    sys.exit(app.exec_())