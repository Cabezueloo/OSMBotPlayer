"""Thread 1 — watch video ads to earn coins."""

import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)

from core.driver import SeleniumDriver
from core.logger import tlog
from bot.helpers import _parse_wait_time, _wait_for_video_end
from locators.html import PLAY_BUTTON_VIDEOS_AD_COINS, CONTENIDO_MENSAJE_DE_ESPERA


def thread_getCoinsWithVideos() -> None:
    """Watch video ads to collect coins (Thread 1)."""
    sd = SeleniumDriver()
    sd.create("https://en.onlinesoccermanager.com/BusinessClub")
    driver = sd.driver

    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element((By.CLASS_NAME, "fc-dialog-overlay"))
            )
            sd.dismiss_popups()
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PLAY_BUTTON_VIDEOS_AD_COINS))
            ).click()
            tlog("Click hecho en el elemento que contiene el video.")

            video_played = _wait_for_video_end(sd, "red")

            if not video_played:
                try:
                    text = driver.find_element(By.XPATH, CONTENIDO_MENSAJE_DE_ESPERA)
                    sleep_s = _parse_wait_time(text, driver)
                    tlog(f"Poniendo en espera {sleep_s // 60} min. Hora: {datetime.now():%H:%M:%S}")
                    time.sleep(sleep_s)
                except NoSuchElementException:
                    sd.refresh_page()

        except (TimeoutException, NoSuchElementException, WebDriverException) as exc:
            tlog(f"Error {type(exc).__name__}: {exc} — URL: {driver.current_url}")
            try:
                driver.save_screenshot("hilo1_error.png")
            except Exception:
                pass
            sd.refresh_page()
