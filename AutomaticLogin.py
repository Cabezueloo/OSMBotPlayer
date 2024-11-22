from SeleniumDriver import SeleniumDriver
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pickle

from utils import COOKIE_USER_ACCOUNT
def automaticLogin(username, password) -> bool:

    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument('--log-level=1') # Para que no salga "Created TensorFlow"
    opts.add_argument("auto-open-devtools-for-tabs")

    #opts.add_argument("--headless")  # Ejecutar en modo headless (Segundo plano)

    opts.add_argument("--mute-audio")  # Silenciar el audio
    opts.add_experimental_option("excludeSwitches", ['enable-logging']) #Only to Chorme
    opts.add_experimental_option('useAutomationExtension', False) #Only to Chorme

    service = Service('chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=opts)
    driver.get('https://en.onlinesoccermanager.com/Login')
    # Inicializar el driver de Chrome
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'
    })

    time.sleep(10)
    boxName = driver.find_element(By.XPATH, "//input[@id='manager-name']")
    boxName.send_keys(username)

    boxPass = driver.find_element(By.XPATH, "//input[@id='password']")
    boxPass.send_keys(password)

    btnLogin = driver.find_element(By.XPATH, "//button[@id='login']")
    btnLogin.click()

    time.sleep(10)

    if str(driver.current_url).split('/')[-1] == 'Dashboard':
        pickle.dump(driver.get_cookies(), open(COOKIE_USER_ACCOUNT, "wb"))
        print("Completed")
        return True
            
    return False




