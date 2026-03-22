"""Application entry point — shows login screen or jumps straight to the Menu."""

import os

from PyQt5.QtWidgets import QApplication, QFormLayout, QLineEdit, QPushButton, QWidget
from PyQt5.QtGui import QFont
from PyQt5 import QtCore

from ui.menu import execMenuApp
from login.auto_login import automaticLogin
from core.config import CREDENTIALS_ACCOUNT_FILE


class Inicio(QWidget):

    if os.path.exists(CREDENTIALS_ACCOUNT_FILE):
        execMenuApp()
        print("pass")

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
            passwordText = self.passwordUser.text()

            credentialsValidate: bool = automaticLogin(usernameText, passwordText)
            print(credentialsValidate)

            if credentialsValidate:
                with open(CREDENTIALS_ACCOUNT_FILE, "x") as f:
                    f.write(usernameText + "\n")
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