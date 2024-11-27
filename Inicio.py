from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 

import os
from hashlib import blake2b

from Menu import execMenuApp
from AutomaticLogin import automaticLogin

from utils import CREDENTIALS_ACCOUNT_FILE



class Inicio(QWidget):

    if os.path.exists(CREDENTIALS_ACCOUNT_FILE):
        execMenuApp()
        print("pass")

    #The user need to login in OSM to get the cookies
    else:
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Requisitos")
            self.resize(100, 100)
            
            self.nameUser = QLineEdit()
            self.nameUser.setFont(QFont("Arial", 10))

            self.passwordUser = QLineEdit()
            
            self.passwordUser.setFont(QFont("Arial", 10))

            self.btnLogin = QPushButton("Aceptar", self)
            
            self.btnLogin.clicked.connect(self.tryLogin)

            flo = QFormLayout()
            flo.addRow("Nombre de entrenador", self.nameUser)
            flo.addRow("Contraseña", self.passwordUser)
            flo.addRow(self.btnLogin)

            self.setLayout(flo)

        def tryLogin(self):

            usernameText = self.nameUser.text()
            print(usernameText)
            passwordText = self.passwordUser.text()
            print(passwordText)
            
            credentialsValidate : bool= automaticLogin(usernameText,passwordText)
            print(credentialsValidate)

            if credentialsValidate:
                f = open(CREDENTIALS_ACCOUNT_FILE,"x")

                f.write(usernameText)
                f.write("\n")
                #print(blake2b(passwordText).hexdigest())
                #passwordHashed = blake2b(passwordText).hexdigest()

                f.write(passwordText)

                QtCore.QCoreApplication.quit()
                execMenuApp()

def execInicioApp():
    app = QApplication([])
    win = Inicio()
    win.show()
    app.exec_()



if __name__ == "__main__":
    execInicioApp()
   
        