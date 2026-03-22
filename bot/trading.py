"""Thread 2 — scan the transfer list, buy undervalued players, list for sale."""

import re
import threading
import time
from datetime import datetime
from itertools import takewhile

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from core.driver import SeleniumDriver
from core.logger import tlog
from bot.helpers import parse_price, get_money_in_account, _safe_int
from bot.selling import thread_sellPlayer
from models.player import Player
from locators.html import (
    TABLA_JUGADORES_EN_VENTA,
    FICHA_JUGADOR_AL_HACER_CLICK_EN_LA_TABLA,
    PRECIO_REAL_JUGADOR_DESDE_LA_FICHA_ABIERTA,
    BOTON_CERRAR_FICHA_JUGADOR_TABLA,
)


def check_available_sell_slots(driver) -> int:
    time.sleep(1)
    text = driver.find_element(By.XPATH, "//li[@id='sell-players-tab']//span").text
    tlog(f"Sell-players tab text: {text!r}")
    match = re.search(r"\d", text)
    if not match:
        tlog("No se encontró número en el tab de venta — asumiendo 0 huecos libres")
        return 0
    return 4 - int(match.group())


def _read_real_price(driver, actions, cell) -> int:
    actions.move_to_element(cell).perform()
    cell.click()
    modal = driver.find_element(By.XPATH, FICHA_JUGADOR_AL_HACER_CLICK_EN_LA_TABLA)
    real_price = 0
    if modal.get_attribute("id") != "modal-dialog-canceltransferplayer":
        raw = modal.find_element(By.XPATH, PRECIO_REAL_JUGADOR_DESDE_LA_FICHA_ABIERTA).get_attribute("innerHTML")
        real_price = parse_price(raw)
    # Close the card
    container = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.ID, "genericModalContainer")))
    WebDriverWait(container, 4).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, BOTON_CERRAR_FICHA_JUGADOR_TABLA))
    ).click()
    return real_price


def _build_player_from_row(driver, actions, cells, budget: int, own_team: str) -> Player | None:
    """Parse a table row into a Player, or return None if it should be skipped."""
    name = cells[0].text.strip()
    if not name:
        return None
    price_text = cells[9].text.replace(",", "").strip()
    if not price_text:
        return None
    price_to_buy = parse_price(price_text)
    if price_to_buy > budget or own_team in cells[4].text:
        return None
    real_price = _read_real_price(driver, actions, cells[0])
    return Player(
        name=name,
        pos=cells[2].text,
        age=cells[3].text,
        club=cells[4].text,
        att=_safe_int(cells[5].text),
        deff=_safe_int(cells[6].text),
        ovr=_safe_int(cells[7].text),
        priceToBuy=price_to_buy,
        realPrice=real_price,
    )


def _purchase_players(driver, sd: SeleniumDriver, names: list[str]) -> None:
    buy_xpath = (
        "//button[contains(@data-bind,'click: buy') and contains(@class, 'btn-success')]"
    )
    for name in names:
        time.sleep(2)
        row = driver.find_element(
            By.XPATH,
            f"//table[contains(@class,'table table-sticky thSortable')]//td[.//span[text()='{name}']]",
        )
        sd.actions.move_to_element(row).click().perform()
        time.sleep(5)
        btn = None
        for _ in range(20):
            btns = driver.find_elements(By.XPATH, buy_xpath)
            for b in btns:
                if b.is_displayed() and b.is_enabled():
                    btn = b
                    break
            if btn:
                break
            time.sleep(0.5)

        if not btn:
            raise TimeoutException("No se encontró el botón de compra visible.")

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(1)
        btn.click()
        tlog(f"Comprado: {name}")
        time.sleep(3)
        sd.refresh_page()


def thread_knowBestBuy(
    min_budget: int = 5_000_000,
    own_team: str = "Inter Milan",
    max_inflation: float = 36.0,  # % — skip players more expensive than this vs real value
) -> None:
    """Scan the transfer list, buy undervalued players, then list them for sale (Thread 2)."""
    sd = SeleniumDriver()
    sd.create("https://en.onlinesoccermanager.com/Transferlist/")
    driver = sd.driver

    while True:
        budget = get_money_in_account(driver)
        tlog(f"Dinero: {budget:,}")
        free_slots = check_available_sell_slots(driver)

        if budget > min_budget and free_slots:
            table = driver.find_element(By.XPATH, TABLA_JUGADORES_EN_VENTA)
            all_rows = (
                row
                for tbody in table.find_elements(By.TAG_NAME, "tbody")
                for row in tbody.find_elements(By.TAG_NAME, "tr")
            )

            candidates: list[Player] = []
            for row in all_rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    continue
                try:
                    player = _build_player_from_row(driver, sd.actions, cells, budget, own_team)
                    if player:
                        candidates.append(player)
                except ValueError as exc:
                    tlog(f"Aviso: ignorando jugador — {exc}")

            candidates.sort()  # Uses Player.__lt__: lowest inflation, highest avg
            for p in candidates:
                tlog(str(p))

            # Select the top N affordable non-inflated players for the available slots
            to_buy: list[str] = []
            rolling_budget = budget
            for player in takewhile(lambda p: p.inflated < max_inflation, candidates[:free_slots]):
                if rolling_budget >= player.priceToBuy:
                    rolling_budget -= player.priceToBuy
                    to_buy.append(player.name)
                else:
                    break

            _purchase_players(driver, sd, to_buy)

            if to_buy:
                sell_thread = threading.Thread(
                    target=thread_sellPlayer, args=(to_buy,), name="Hilo 3", daemon=True
                )
                tlog("Iniciado controlador de poner jugadores comprados a vender")
                sell_thread.start()
                sell_thread.join()

        else:
            reason = "Dinero insuficiente" if budget < min_budget else "No hay huecos de venta (4/4 ocupado)"
            tlog(reason)

        tlog(f"Esperando 30 min. Hora: {datetime.now():%H:%M:%S}")
        time.sleep(1_800)
        sd.refresh_page()
