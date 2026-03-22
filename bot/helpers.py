"""Shared helpers used by multiple bot threads."""

import re
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)

from core.logger import tlog

# ---------------------------------------------------------------------------
# Price parsing
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


def _safe_int(value: str) -> int:
    v = value.strip()
    return int(v) if v and v != "-" and v.isdigit() else 0


# ---------------------------------------------------------------------------
# Wait-time parser (OSM "come back in X" modal)
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
# Video-ad waiter
# ---------------------------------------------------------------------------

def _wait_for_video_end(sd, color: str) -> bool:
    """Wait until #videoad is hidden; reload if stuck > 2 min. Returns True if a video played."""
    driver = sd.driver
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
            sd.refresh_page()
            return False

    return elapsed > 0  # True if video actually played
