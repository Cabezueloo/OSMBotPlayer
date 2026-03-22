"""PyQt5 front-end for the OSM bot — parameter configuration and thread management."""

import json
import sys
import threading
import time

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QWidget,
)

from bot.videos import thread_getCoinsWithVideos
from bot.trading import thread_knowBestBuy
from bot.training import thread_trainingPlayers
from core.config import (
    COOKIE_USER_ACCOUNT,
    CREDENTIALS_ACCOUNT_FILE,
    MIN_MONEY,
    NAME_TEAM,
    OPTIONS_MENU,
    REDIRECTION,
    TRADING,
    TRAINING_PLAYERS,
    VIDEO_COINS,
)

_THREAD_DEFS = [
    # (attr_name,                thread_name, target,                    extra_args_fn)
    ("checkbox_video_monedas",   "Hilo 1", thread_getCoinsWithVideos,  lambda s: ()),
    ("checkbox_compra_venta",    "Hilo 2", thread_knowBestBuy,         lambda s: (int(s.millonesCompraVenta.text()), s.nombreEquipo.text())),
    ("checkbox_control_jugadores", "Hilo 4", thread_trainingPlayers,   lambda s: ()),
]


class Menu(QWidget):
    update_out_text_signal = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Parámetros del BOT")
        self.resize(400, 400)

        font = QFont("Arial", 10)
        self.nombreEquipo = QLineEdit()
        self.nombreEquipo.setFont(font)

        self.millonesCompraVenta = QLineEdit()
        self.millonesCompraVenta.setValidator(QIntValidator())
        self.millonesCompraVenta.setFont(font)

        self.checkbox_video_monedas      = QCheckBox("Ver videos automáticamente para conseguir monedas")
        self.checkbox_compra_venta       = QCheckBox("Control de compra-venta de jugadores")
        self.checkbox_control_jugadores  = QCheckBox("Control de entrenar jugadores")

        checks_layout = QHBoxLayout()
        for cb in (self.checkbox_video_monedas, self.checkbox_compra_venta, self.checkbox_control_jugadores):
            checks_layout.addWidget(cb)

        btn_start  = QPushButton("Start")
        btn_logout = QPushButton("Log Out")
        btn_close  = QPushButton("Close")
        btn_start.clicked.connect(self._on_start)
        btn_logout.clicked.connect(self._on_logout)
        btn_close.clicked.connect(sys.exit)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(btn_logout)
        bottom_layout.addWidget(btn_close)

        self.outTextBot = QTextEdit()
        self.outTextBot.setFixedSize(600, 200)
        self.update_out_text_signal.connect(self.outTextBot.setText)

        layout = QFormLayout()
        layout.addRow("Nombre del equipo", self.nombreEquipo)
        layout.addRow("Mínimo millones para operar", self.millonesCompraVenta)
        layout.addRow(checks_layout)
        layout.addRow(btn_start)
        layout.addRow(bottom_layout)
        layout.addRow(self.outTextBot)
        self.setLayout(layout)

        if OPTIONS_MENU.exists():
            self._restore_last_options()

    # ------------------------------------------------------------------ #
    # Options persistence                                                  #
    # ------------------------------------------------------------------ #

    def _restore_last_options(self) -> None:
        data: dict = json.loads(OPTIONS_MENU.read_text())
        self.nombreEquipo.setText(data.get(NAME_TEAM, ""))
        self.millonesCompraVenta.setText(data.get(MIN_MONEY, ""))
        self.checkbox_video_monedas.setChecked(data.get(VIDEO_COINS, False))
        self.checkbox_compra_venta.setChecked(data.get(TRADING, False))
        self.checkbox_control_jugadores.setChecked(data.get(TRAINING_PLAYERS, False))

    def _save_options(self) -> None:
        OPTIONS_MENU.parent.mkdir(parents=True, exist_ok=True)
        OPTIONS_MENU.write_text(json.dumps({
            NAME_TEAM:        self.nombreEquipo.text(),
            MIN_MONEY:        self.millonesCompraVenta.text(),
            VIDEO_COINS:      self.checkbox_video_monedas.isChecked(),
            TRADING:          self.checkbox_compra_venta.isChecked(),
            TRAINING_PLAYERS: self.checkbox_control_jugadores.isChecked(),
        }, indent=2))

    # ------------------------------------------------------------------ #
    # Button handlers                                                      #
    # ------------------------------------------------------------------ #

    def _on_logout(self) -> None:
        for path in (CREDENTIALS_ACCOUNT_FILE, COOKIE_USER_ACCOUNT):
            path.unlink(missing_ok=True)

    def _on_start(self) -> None:
        self._save_options()
        for attr, name, target, args_fn in _THREAD_DEFS:
            if getattr(self, attr).isChecked():
                print(f"Iniciando {name} — {target.__name__}")
                threading.Thread(
                    target=target, args=args_fn(self), name=name, daemon=True
                ).start()

    # ------------------------------------------------------------------ #
    # Output monitor                                                       #
    # ------------------------------------------------------------------ #

    def _monitor_output(self) -> None:
        while True:
            time.sleep(10)
            try:
                text = REDIRECTION.read_text()
                if text:
                    self.update_out_text_signal.emit(text)
            except Exception:
                pass


def execMenuApp() -> None:
    app = QApplication(sys.argv)
    win = Menu()
    threading.Thread(target=win._monitor_output, daemon=True).start()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    execMenuApp()
