"""Control of buy-sell, training, and video-coin farming for OSM via Selenium + threading."""

import re
import sys
import threading
import time
from datetime import datetime, timedelta
from itertools import takewhile

import random
from termcolor import colored
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
    StaleElementReferenceException,
)

from Player import Player
from RutuasAlHTML import (
    PLAY_BUTTON_VIDEOS_AD_COINS,
    CONTENIDO_MENSAJE_DE_ESPERA,
    TABLA_JUGADORES_EN_VENTA,
    FICHA_JUGADOR_AL_HACER_CLICK_EN_LA_TABLA,
    PRECIO_REAL_JUGADOR_DESDE_LA_FICHA_ABIERTA,
    BOTON_CERRAR_FICHA_JUGADOR_TABLA,
    BOTON_CONFIRMAR_PONER_A_LA_VENTA,
    BOTON_VER_ANUNCIO_JUGADORES_ENTRENANDO,
    BOTON_COMPLETE_DE_LOS_ENTRENAMIENTOS,
    BOTON_START_PONER_JUGADOR_A_ENTRENAR,
    BOTON_OK_MENSAJE_CONFIRMACION_PONER_JUGADOR_A_ENTRENAR,
)
from SeleniumDriver import SeleniumDriver
from utils import REDIRECTION

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_THREAD_COLORS = {"Hilo 1": "red", "Hilo 2": "green", "Hilo 3": "blue", "Hilo 4": "yellow"}


def log(msg: str, color: str = "white") -> None:
    """Thread-safe colored log; also appends to REDIRECTION file."""
    line = f"{threading.current_thread().name}-> {msg}"
    print(colored(line, color))
    REDIRECTION.parent.mkdir(parents=True, exist_ok=True)
    with REDIRECTION.open("a") as fh:
        fh.write(line + "\n")


def tlog(msg: str) -> None:
    """Log using the current thread's canonical color."""
    log(msg, _THREAD_COLORS.get(threading.current_thread().name, "white"))


# ---------------------------------------------------------------------------
# Price parsing helpers
# ---------------------------------------------------------------------------

_SUFFIXES: dict[str, int] = {"M": 1_000_000, "K": 1_000}


def parse_price(raw: str) -> int:
    """'14.5M' → 14_500_000; '500K' → 500_000; '750000' → 750_000."""
    text = raw.replace(",", "").strip()
    for suffix, multiplier in _SUFFIXES.items():
        if suffix in text:
            return int(float(text.replace(suffix, "")) * multiplier)
    return int(float(text)) if text else 0


def get_money_in_account(driver) -> int:
    span = driver.find_element(
        By.CSS_SELECTOR,
        'div.clubfunds-wallet span[data-bind*="animatedProgress"]',
    )
    return parse_price(span.get_attribute("innerHTML"))


# ---------------------------------------------------------------------------
# Transfer-list helpers
# ---------------------------------------------------------------------------

def check_available_sell_slots(driver) -> int:
    time.sleep(1)
    text = driver.find_element(By.XPATH, "//li[@id='sell-players-tab']//span").text
    tlog(f"Sell-players tab text: {text!r}")
    match = re.search(r"\d", text)
    if not match:
        tlog("No se encontró número en el tab de venta — asumiendo 0 huecos libres")
        return 0
    return 4 - int(match.group())


def _safe_int(value: str) -> int:
    v = value.strip()
    return int(v) if v and v != "-" and v.isdigit() else 0


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


# ---------------------------------------------------------------------------
# Thread: video coins
# ---------------------------------------------------------------------------

def _wait_for_video_end(driver, color: str) -> bool:
    """Wait until #videoad is hidden; reload if stuck > 2 min. Returns True if a video played."""
    time.sleep(5)
    try:
        video_ad = driver.find_element(By.ID, "videoad")
    except NoSuchElementException:
        return False

    elapsed = 0
    while True:
        try:
            if not video_ad.is_displayed():
                break
        except (StaleElementReferenceException, NoSuchElementException):
            break

        tlog("El video no ha terminado")
        time.sleep(15)
        elapsed += 15
        if elapsed >= 120:
            tlog("El video se ha atascado por más de 2 minutos. Recargando página...")
            driver.refresh()
            return False

    return elapsed > 0  # True if video actually played


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
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PLAY_BUTTON_VIDEOS_AD_COINS))
            ).click()
            tlog("Click hecho en el elemento que contiene el video.")

            video_played = _wait_for_video_end(driver, "red")

            if not video_played:
                try:
                    text = driver.find_element(By.XPATH, CONTENIDO_MENSAJE_DE_ESPERA)
                    sleep_s = _parse_wait_time(text, driver)
                    tlog(f"Poniendo en espera {sleep_s // 60} min. Hora: {datetime.now():%H:%M:%S}")
                    time.sleep(sleep_s)
                except NoSuchElementException:
                    driver.refresh()

        except (TimeoutException, NoSuchElementException, WebDriverException) as exc:
            tlog(f"Error {type(exc).__name__}: {exc} — URL: {driver.current_url}")
            try:
                driver.save_screenshot("hilo1_error.png")
            except Exception:
                pass
            driver.refresh()


# ---------------------------------------------------------------------------
# Thread: buy-sell
# ---------------------------------------------------------------------------

def thread_knowBestBuy(
    min_budget: int = 5_000_000,
    own_team: str = "Inter Milan",
    max_inflation: float = 36.0,   # % — skip players more expensive than this vs real value
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


def _purchase_players(driver, sd: SeleniumDriver, names: list[str]) -> None:
    buy_xpath = (
        "//button[contains(@data-bind,'click: buy') and contains(@class, 'btn-success')]"
    )
    for name in names:
        time.sleep(2)
        row = driver.find_element(By.XPATH, f"//table[contains(@class,'table table-sticky thSortable')]//td[.//span[text()='{name}']]")
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


# ---------------------------------------------------------------------------
# Thread: sell
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Thread: training
# ---------------------------------------------------------------------------

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
                video_played = _wait_for_video_end(driver, "yellow")
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


def _complete_and_assign_training(driver) -> None:
    """Click all 'Complete' buttons, then assign players to empty slots."""
    # Complete finished trainings
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
        hrs = int(re.search(r"(\d+)h", text).group(1)) if "h" in text else 0
        mnt = int(re.search(r"(\d+)m", text).group(1)) if "m" in text else 0
        hours = (days * 24) + hrs
        minutes = mnt
    except Exception as e:
        tlog(f"Aviso: No se pudo leer el tiempo restante real ({e}). Asumiendo 8h+")
        hours = 8
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


# ---------------------------------------------------------------------------
# Wait-time parser
# ---------------------------------------------------------------------------

def _parse_wait_time(text_elem, driver) -> int:
    """Read the OSM 'come back in X' message and return seconds to sleep."""
    html = text_elem.get_attribute("innerHTML").lower()
    tlog(html)

    digits = re.findall(r"\d+", html)
    val = int(digits[0]) if digits else 0

    if "second" in html:
        seconds = val if val > 0 else 120
    elif "minute" in html:
        seconds = (val * 60) if val > 0 else 120
    elif "an hour" in html:
        seconds = 3600
    elif "hour" in html:
        seconds = (val * 3600) if val > 0 else 3600
    else:
        tlog("No se reconoció el formato de tiempo. Asumiendo 10 min.")
        seconds = 600

    try:
        driver.find_element(
            By.XPATH, "//div[contains(@id,'modal-dialog-alert')]//button[contains(@class,'close')]"
        ).click()
        tlog("Ventana de espera cerrada")
    except Exception as exc:
        tlog(f"No se encontró el botón close: {exc}")

    return seconds


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = sys.argv[1:]
    own_team  = args[0]       if len(args) > 0 else "Inter Milan"
    min_money = int(args[1])  if len(args) > 1 else 25_000_000
    do_coins  = eval(args[2]) if len(args) > 2 else True
    do_trade  = eval(args[3]) if len(args) > 3 else True
    do_train  = eval(args[4]) if len(args) > 4 else True

    # List of tuples — a dict keyed on bool would silently merge entries
    thread_defs = [
        (do_coins, "Hilo 1", thread_getCoinsWithVideos, ()),
        (do_trade, "Hilo 2", thread_knowBestBuy,        (min_money, own_team)),
        (do_train, "Hilo 4", thread_trainingPlayers,    ()),
    ]

    active_threads: list[threading.Thread] = []
    for enabled, name, target, targs in thread_defs:
        if enabled:
            print(f"Iniciando {name} — {target.__name__}")
            t = threading.Thread(target=target, args=targs, name=name, daemon=False)
            t.start()
            active_threads.append(t)

    # Keep the main thread alive until every bot thread finishes (or Ctrl-C)
    try:
        for t in active_threads:
            t.join()
    except KeyboardInterrupt:
        print("Bot detenido manualmente.")
