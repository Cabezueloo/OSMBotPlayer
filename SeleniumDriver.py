"""Selenium driver wrapper with automatic cookie/popup handling."""

import pickle
import platform
import random
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils import COOKIE_USER_ACCOUNT

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/83.0.4103.53 Safari/537.36"
)


class SeleniumDriver:
    """Thin wrapper around a Selenium Chrome driver with OSM-specific helpers."""

    def __init__(self, modoVerActivado: bool = False) -> None:
        opts = Options()
        for arg in ("--start-maximized", "--log-level=1", "--mute-audio"):
            opts.add_argument(arg)
        opts.add_experimental_option("excludeSwitches", ["enable-logging"])
        opts.add_experimental_option("useAutomationExtension", False)

        service = (
            Service("chromedriver.exe")
            if platform.system() == "Windows"
            else webdriver.ChromeService()
        )
        self.driver = webdriver.Chrome(service=service, options=opts)
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride", {"userAgent": _USER_AGENT}
        )
        self.actions = ActionChains(self.driver)

    # ------------------------------------------------------------------ #
    # Navigation                                                           #
    # ------------------------------------------------------------------ #

    def load_url(self, url: str) -> None:
        self.url = url
        self.driver.get(url)

    def load_cookies(self) -> None:
        if not COOKIE_USER_ACCOUNT.exists():
            print(f"[SeleniumDriver] Cookie file not found ({COOKIE_USER_ACCOUNT}). Run Login.py first.")
            return
        for cookie in pickle.loads(COOKIE_USER_ACCOUNT.read_bytes()):
            self.driver.add_cookie(cookie)

    def refresh_page(self) -> None:
        time.sleep(5)
        self.driver.get(self.url)
        time.sleep(6)
        self._dismiss_popups()

    def create(self, url: str) -> None:
        self.load_url(url)
        self.load_cookies()
        self.refresh_page()

    def close(self) -> None:
        self.driver.quit()

    # ------------------------------------------------------------------ #
    # Internal popup-dismissal helpers                                     #
    # ------------------------------------------------------------------ #

    def _dismiss_popups(self) -> None:
        """Silently dismiss every known OSM overlay in one pass."""
        self._try_click(By.XPATH, "//button[contains(@class,'fc-cta-consent')]/p")
        self._try_wait_click(By.XPATH, "//div[@id='modal-dialog-centerpopup']//button[@class='close']/span")
        self._dismiss_skill_update_modal()

    def _try_click(self, by: str, locator: str) -> None:
        try:
            self.driver.find_element(by, locator).click()
        except Exception:
            pass

    def _try_wait_click(self, by: str, locator: str, timeout: int = 3) -> None:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            ).click()
        except Exception:
            pass

    def _dismiss_skill_update_modal(self) -> None:
        try:
            modal = self.driver.find_element(By.ID, "modal-dialog-skillratingupdate")
            if not modal.is_displayed():
                return
            loc  = modal.location
            size = modal.size
            w    = self.driver.execute_script("return window.innerWidth")
            h    = self.driver.execute_script("return window.innerHeight")

            # Pick a random point guaranteed to be outside the modal bounds
            x, y = next(
                (rx, ry)
                for rx in (random.randint(0, w),)
                for ry in (random.randint(0, h),)
                if not (loc["x"] <= rx <= loc["x"] + size["width"]
                        and loc["y"] <= ry <= loc["y"] + size["height"])
            )
            self.actions.move_by_offset(x, y).click().perform()
        except Exception:
            pass
