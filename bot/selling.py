"""Thread 3 — list purchased players on the transfer market."""

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.driver import SeleniumDriver
from core.logger import tlog


def thread_sellPlayer(players_to_sell: list[str]) -> None:
    """List purchased players on the transfer market (Thread 3)."""
    sd = SeleniumDriver()
    sd.create("https://en.onlinesoccermanager.com/Transferlist#sell-players")
    driver = sd.driver

    sell_buttons = driver.find_elements(
        By.XPATH,
        "//div[contains(@class,'sell-player-slot-container')]"
        "//button[contains(@data-bind,'showSelectSellPlayerModal')]",
    )

    for btn, name in zip(sell_buttons, players_to_sell):
        time.sleep(1)
        btn.click()
        time.sleep(3)
        driver.find_element(By.XPATH, f"//td[.//span[text()='{name}']]").click()

        slider = WebDriverWait(driver, 6).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".slider-handle.min-slider-handle"))
        )
        time.sleep(1)
        sd.actions.click_and_hold(slider).move_by_offset(400, 0).release().perform()

        confirm_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@data-bind,'click: sell')]"))
        )
        time.sleep(1)
        confirm_btn.click()

        tlog(f"Jugador {name} puesto en venta")
        time.sleep(3)
