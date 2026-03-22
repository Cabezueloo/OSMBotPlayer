"""Automatic login: fills credentials on OSM and saves session cookies."""

import pickle
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from core.config import COOKIE_USER_ACCOUNT

_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/83.0.4103.53 Safari/537.36"
)


def _build_driver() -> webdriver.Chrome:
    opts = Options()
    for arg in ("--start-maximized", "--log-level=1", "--mute-audio"):
        opts.add_argument(arg)
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=Service(), options=opts)
    driver.execute_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": _USER_AGENT})
    driver.implicitly_wait(10)
    return driver


def automaticLogin(username: str, password: str) -> bool:
    """Return True and persist cookies if login succeeds, False otherwise."""
    driver = _build_driver()
    driver.get("https://en.onlinesoccermanager.com/Login")

    driver.find_element(By.XPATH, "//button[@class='btn-new btn-orange']//span[@class='font-md']").click()
    driver.find_element(By.XPATH, "//button[@data-bind='click: goToLogin']").click()
    driver.find_element(By.ID, "manager-name").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login").click()

    time.sleep(5)
    if driver.current_url.split("/")[-1] == "Dashboard":
        COOKIE_USER_ACCOUNT.parent.mkdir(parents=True, exist_ok=True)
        COOKIE_USER_ACCOUNT.write_bytes(pickle.dumps(driver.get_cookies()))
        print("Login completed.")
        return True

    driver.quit()
    return False
