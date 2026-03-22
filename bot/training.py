"""Thread 4 — manage player training and watch training ads."""

import re
import time
from datetime import datetime

from selenium.webdriver.common.by import By

from core.driver import SeleniumDriver
from core.logger import tlog
from bot.helpers import _parse_wait_time, _wait_for_video_end
from locators.html import (
    BOTON_VER_ANUNCIO_JUGADORES_ENTRENANDO,
    BOTON_COMPLETE_DE_LOS_ENTRENAMIENTOS,
    BOTON_START_PONER_JUGADOR_A_ENTRENAR,
    BOTON_OK_MENSAJE_CONFIRMACION_PONER_JUGADOR_A_ENTRENAR,
    CONTENIDO_MENSAJE_DE_ESPERA,
)


def _get_training_seconds_remaining(driver) -> int:
    """Return seconds left on the active training timer (h1.timer), or 0 if not visible."""
    try:
        el = driver.find_element(
            By.CSS_SELECTOR,
            'h1.timer[data-bind*="secondsRemaining"]',
        )
        if not el.is_displayed():
            return 0
        text = el.text.strip()  # e.g. '01h 25m 59s'
        days = int(re.search(r"(\d+)d", text).group(1)) if "d" in text else 0
        hrs  = int(re.search(r"(\d+)h", text).group(1)) if "h" in text else 0
        mnt  = int(re.search(r"(\d+)m", text).group(1)) if "m" in text else 0
        sec  = int(re.search(r"(\d+)s", text).group(1)) if "s" in text else 0
        return days * 86_400 + hrs * 3_600 + mnt * 60 + sec
    except Exception:
        return 0


def _complete_and_assign_training(driver) -> None:
    """Click all 'Complete' buttons, then assign players to empty slots."""
    for btn in driver.find_elements(By.XPATH, BOTON_COMPLETE_DE_LOS_ENTRENAMIENTOS):
        btn.click()
        time.sleep(2)
        tlog("Botón de entrenamiento completado pulsado")
    time.sleep(15)

    try:
        timer_span = driver.find_element(By.CSS_SELECTOR, 'span[data-bind="time: secondsRemaining"]')
        text = timer_span.get_attribute("textContent").strip()
        # Expected format: '02d 07h 25m 29s' or '07h 25m 29s'
        days = int(re.search(r"(\d+)d", text).group(1)) if "d" in text else 0
        hrs  = int(re.search(r"(\d+)h", text).group(1)) if "h" in text else 0
        mnt  = int(re.search(r"(\d+)m", text).group(1)) if "m" in text else 0
        hours   = (days * 24) + hrs
        minutes = mnt
    except Exception as e:
        tlog(f"Aviso: No se pudo leer el tiempo restante real ({e}). Asumiendo 8h+")
        hours   = 8
        minutes = 0
    tlog(f"Tiempo hasta el partido: {hours}h {minutes}m")

    add_buttons = driver.find_elements(By.XPATH, BOTON_START_PONER_JUGADOR_A_ENTRENAR)

    match hours:
        case h if h > 7:
            for btn in add_buttons:
                btn.click()
                time.sleep(1)
                rows = driver.find_elements(By.XPATH, "//table[contains(@id,'squad-table')]//tr")
                rows[1].click()  # always pick row index 1 (first player)
                tlog(f"Jugador añadido a {hours}h {minutes}m del partido")
                time.sleep(1)
                try:
                    driver.find_element(By.XPATH, BOTON_OK_MENSAJE_CONFIRMACION_PONER_JUGADOR_A_ENTRENAR).click()
                    time.sleep(5)
                except Exception:
                    print("Modal de confirmación no presente.")
        case _ if len(add_buttons) == 4:
            wait_s = (hours * 3600) + (minutes * 60) + 1_800  # sleep until match + 30 min buffer
            tlog(f"Pausado — sin entrenamientos activos. Esperando {hours}h {minutes}m")
            time.sleep(wait_s)
        case _:
            tlog("Diferencia < 7h — no se añaden jugadores")


def thread_trainingPlayers() -> None:
    """Manage player training and watch training ads (Thread 4)."""
    sd = SeleniumDriver()
    sd.create("https://en.onlinesoccermanager.com/Training")
    driver = sd.driver

    while True:
        _complete_and_assign_training(driver)
        try:
            for index, btn in enumerate(driver.find_elements(By.XPATH, BOTON_VER_ANUNCIO_JUGADORES_ENTRENANDO)):
                btn.click()
                tlog(f"Click en botón de anuncio #{index}")
                video_played = _wait_for_video_end(sd, "yellow")
                if not video_played:
                    try:
                        text = driver.find_element(By.XPATH, CONTENIDO_MENSAJE_DE_ESPERA)
                        cooldown_s = _parse_wait_time(text, driver)
                        training_s = _get_training_seconds_remaining(driver)
                        if training_s > 0 and training_s < cooldown_s:
                            sleep_s = training_s
                            tlog(
                                f"Entrenamiento termina antes ({training_s // 60}m) "
                                f"que el cooldown ({cooldown_s // 60}m) — "
                                f"esperando hasta fin de entrenamiento. Hora: {datetime.now():%H:%M:%S}"
                            )
                        else:
                            sleep_s = cooldown_s
                            tlog(f"Esperando {sleep_s // 60} min. Hora: {datetime.now():%H:%M:%S}")
                        time.sleep(sleep_s)
                        sd.refresh_page()
                    except Exception:
                        break
                else:
                    _complete_and_assign_training(driver)
        except Exception:
            pass
