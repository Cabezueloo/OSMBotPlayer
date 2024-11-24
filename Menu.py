from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
import sys
from utils import *
import os 
import threading 
from main import thread_getCoinsWithVideos,thread_knowBestBuy,thread_trainingPlayers

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
        self.checkbox_video_monedas.setChecked(False)

        self.checkbox_compra_venta = QCheckBox('Control de compra-venta de jugadoes', self)
        self.checkbox_compra_venta.setChecked(False)

        self.checkbox_control_jugadores = QCheckBox('Control de entrenar jugadores', self)
        self.checkbox_control_jugadores.setChecked(False)

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

        if os.path.exists(OPTIONS_MENU):
            self.lastOptionsMarked()
        
        self.setLayout(flo)

        

    def lastOptionsMarked(self):
        file=open(OPTIONS_MENU,"r")

        text = file.read()

        dictionari :dict = eval(text)
        self.nombreEquipo.setText(dictionari.get(NAME_TEAM))
        self.millonesCompraVenta.setText(dictionari.get(MIN_MONEY))

        if eval(dictionari.get(VIDEO_COINS)):
            self.checkbox_video_monedas.setChecked(True)

        if eval(dictionari.get(TRADING)):
            self.checkbox_compra_venta.setChecked(True)

        if eval(dictionari.get(TRAINING_PLAYERS)):
            self.checkbox_control_jugadores.setChecked(True)



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

        if not os.path.exists(OPTIONS_MENU):
            f = open(OPTIONS_MENU,"x")
        else:
           f = open(OPTIONS_MENU,"w") 
               
        
        f.write("{\n'"+NAME_TEAM+"':'"+nombreEquipo+"',\n")
        f.write("'"+MIN_MONEY+"':'"+str(millonesMinimos)+"',\n")
        f.write("'"+VIDEO_COINS+"':'"+str(controlVideoMonedas)+"',\n")
        f.write("'"+TRADING+"':'"+str(controlCompraVenta)+"',\n")
        f.write("'"+TRAINING_PLAYERS+"':'"+str(controlEntrenamientoJugadores)+"'\n}")

        # Ejecutar el bot con los parámetros introducidos
        self.setEnabled(False)
        self.setVisible(False)

        
        # Crear los hilos y ejecutar
        threadOneControlOfCoinsVideos = threading.Thread(target=thread_getCoinsWithVideos,name="Hilo 1")
        threadTwoControlOfTransferList = threading.Thread(target=thread_knowBestBuy,args=(millonesMinimos,nombreEquipo,),name="Hilo 2")
        #HILO PONE EN VENTA A LOS JUGADORES COMPRADOS DEL HILO DOS, SE CREA DESDE EL HILO 2
        threadFourControlOfTrainingPlayers = threading.Thread(target=thread_trainingPlayers, name="Hilo 4")
        
        # Iniciar los hilos
        if controlVideoMonedas:
            print("Iniciado controlador de video monedas")
            threadOneControlOfCoinsVideos.start()
        if controlCompraVenta:
            print("Iniciado controlador de compra-venta")
            threadTwoControlOfTransferList.start()
        if controlEntrenamientoJugadores:
            print("Iniciado controlador de entrenamiento de jugadores")
            threadFourControlOfTrainingPlayers.start()


        # Volver a habilitar el menú una vez termine el bot
        self.setEnabled(True)
        self.setVisible(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Menu()
    win.show()
    sys.exit(app.exec_())