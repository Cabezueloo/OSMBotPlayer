
import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import platform
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random


class SeleniumDriver:
    def __init__(self):
        # Configuración de opciones de Chrome
        self.opts = Options()
        self.opts.add_argument("--start-maximized")
        self.opts.add_argument('--log-level=1') # Para que no salga "Created TensorFlow"

        #self.opts.add_argument("--headless")  # Ejecutar en modo headless (Segundo plano)
        self.opts.add_argument("--mute-audio")  # Silenciar el audio
        self.opts.add_experimental_option("excludeSwitches", ['enable-logging']) 
        self.opts.add_experimental_option('useAutomationExtension', False)
        

        # Crear un servicio para el chromedriver
        if platform.system()=="Windows":
            self.service = Service('chromedriver.exe')
        elif platform.system()=="Linux":
            self.opts.binary_location = '/usr/bin/chromium-browser'
            self.service = Service('/usr/bin/chromedriver')

        # Inicializar el driver de Chrome
        self.driver = webdriver.Chrome(service=self.service, options=self.opts)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'
        })

    def load_url(self, url):
        # Entrar a la URL
        self.driver.get(url)
        self.url = url

    def load_cookies(self):
        # Cargar las cookies
        cookies = pickle.load(open("cookie.pkl", "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def refresh_page(self):
        # Esperar y recargar la URL
        time.sleep(5)
        self.driver.get(self.url)
        time.sleep(6)

        #Check if a OSM ask personal data
        try:
            btn = self.driver.find_element(By.XPATH, "//button[contains(@class, 'fc-button fc-cta-consent fc-primary-button')]/p")
      
            btn.click()
            time.sleep(2)
        except:
            pass
        
        #Check if a pop-up show
        try:
            span_element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='modal-dialog-centerpopup']//button[@class='close']/span"))
            )
            
            span_element.click()
        except Exception:
            pass
        
        try:
            #Check if a modal-dialog-skillratingupdate
            modal = self.driver.find_element(By.ID, "modal-dialog-skillratingupdate")
            
            # Verifica si el modal es visible
            if modal.is_displayed():
                # Obtiene la posición y dimensiones del modal
                modal_location = modal.location
                modal_size = modal.size
                modal_left = modal_location['x']
                modal_top = modal_location['y']
                modal_right = modal_left + modal_size['width']
                modal_bottom = modal_top + modal_size['height']
                
                # Genera una posición aleatoria fuera del modal
                window_width = self.driver.execute_script("return window.innerWidth")
                window_height = self.driver.execute_script("return window.innerHeight")

                # Asegurarse de que el clic sea fuera de los límites del modal
                while True:
                    random_x = self.driver.randint(0, window_width)
                    random_y = random.randint(0, window_height)
                    
                    if not (modal_left <= random_x <= modal_right and modal_top <= random_y <= modal_bottom):
                        break

                # Simula un clic en la posición aleatoria fuera del modal
                
                self.actions.move_by_offset(random_x, random_y).click().perform()
                print("Modal cerrado con clic en posición aleatoria fuera del modal:", (random_x, random_y))
        except Exception:
            pass
            #print(f"modal dialog skillratingupdate no encontrado")

    def close(self):
        self.driver.quit()
    
    def actions(self):
        self.actions = ActionChains(self.driver)
