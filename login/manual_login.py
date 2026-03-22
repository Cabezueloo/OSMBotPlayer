"""Manual login script — opens a visible browser and waits for the user to log in,
then saves the session cookies so the bot can reuse them."""

import pickle

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from core.config import COOKIE_USER_ACCOUNT

opts = Options()
opts.add_argument("start-maximized")
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option("useAutomationExtension", False)


def run_manual_login() -> None:
    """Open a browser window and wait until the user reaches the Dashboard, then save cookies."""
    service = Service()
    print("Esperando")
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd(
        "Network.setUserAgentOverride",
        {
            "userAgent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/83.0.4103.53 Safari/537.36"
            )
        },
    )
    driver.get("https://en.onlinesoccermanager.com/")

    while True:
        try:
            driver.get_window_size()
            if str(driver.current_url).split("/")[-1] == "Dashboard":
                COOKIE_USER_ACCOUNT.parent.mkdir(parents=True, exist_ok=True)
                COOKIE_USER_ACCOUNT.write_bytes(pickle.dumps(driver.get_cookies()))
                print("Completed")
                break
        except exceptions.WebDriverException:
            break


if __name__ == "__main__":
    run_manual_login()
