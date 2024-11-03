'''Control of the account using Selenium and threading'''


import threading
import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Player import Player
import re
from SeleniumDriver import SeleniumDriver


def thread_getCoinsWithVideos():

    '''Hilo encargado de ver videos siempre que se pueda para recopilar monedas'''
    
    selenium_driver  = SeleniumDriver()
    selenium_driver.load_url("https://en.onlinesoccermanager.com/BusinessClub")
    selenium_driver.load_cookies()
    selenium_driver.refresh_page()

    driver = selenium_driver.driver
    

    while True:
        try:
            # Esperar hasta que el elemento que reproduce el video sea clickeable
            play_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".row.row-h-xs-150.row-h-sm-24.business-club-method-container.method-container-small.center.watchvideo-method"))
            )

            # Hacer clic en el elemento para reproducir el video
            play_button.click()
            print("Click hecho en el elemento que contiene el video.")

            # Esperar hasta que el video haya terminado
            while True:
                try:
                    # Esperar un corto período de tiempo y verificar el estado del video
                    time.sleep(1)  # Ajusta este tiempo según la duración de tu espera
                    # Verificar si el div de video ha cambiado a inactivo
                    video_ad = driver.find_element(By.ID, "videoad")

                    outer_html = video_ad.get_attribute("outerHTML")
                    



                    # Comprobar el estado del div
                    if len(outer_html) == 24 or video_ad.value_of_css_property('display') == 'none':
                        print("El video ha terminado o no ha cargado")
                        break
                except Exception:
                    print("No se pudo verificar el estado del video, asumiendo que ha terminado.")
                    break



            try:
                text = driver.find_element(By.XPATH, "//p[@data-bind='html: content']")
                timeToSleep = getTimeToSleep(text,driver)

                print(f"Esperar tiempo de {timeToSleep/60} minutos")
            
                
                
                time.sleep(timeToSleep)
                driver.refresh()

            except Exception:
                pass

            
        except Exception as e:
            print(f"Error{e}")
            break

def thread_knowBestBuy():
    selenium_driver  = SeleniumDriver()
    selenium_driver.load_url("https://en.onlinesoccermanager.com/Transferlist/")
    selenium_driver.load_cookies()
    selenium_driver.refresh_page()
    

    
    while True:
        driver = selenium_driver.driver
        #Dinero en la cuenta
        span_element = driver.find_element(By.CSS_SELECTOR, 
            'span[data-bind="currency: $parent.shouldShowSavings() ? $parent.savings() : animatedProgress(), roundCurrency: RoundCurrency.Downwards, fractionDigitsK: 1, fractionDigits: 1"]')
        dinero = int(float(span_element.get_attribute("innerHTML").replace("M", "")) * 1000000)
        
        print(f'Dinero que tengo es de:{dinero} ')

        if dinero>10000000:
            # Encontrar la tabla por su clase
            table = driver.find_element(By.XPATH, '//table[contains(@class, "table table-sticky thSortable")]')

            # Encontrar todos los tbody dentro de la tabla

            tbody_elements = table.find_elements(By.TAG_NAME, 'tbody')

            #Cada row es un jugador y cada celda guarda un dato
            #row0 -> Name of the player
            #row1 -> None
            #row2 -> Position he plays
            #row3 -> Age
            #row4 -> That club he pertence
            #row5 -> Points of Att
            #row6 -> Points of Def
            #row7 -> Points of Ovr
            #row8 -> None
            #row9 -> Price in String, for this the replace of a "M"

            # Iterar sobre cada tbody

            listaJugadores = []

            for tbody in tbody_elements:
                # Encontrar todas las filas dentro del tbody
                rows = tbody.find_elements(By.TAG_NAME, 'tr')
                for row in rows:
                    # Extraer datos de cada celda dentro de la fila
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    row.click()
                    player_profile_div = WebDriverWait(driver, 0.5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "player-profile-value"))
                    )

                    span = player_profile_div.find_elements(By.TAG_NAME, "span")[1]

                    price :str = span.get_attribute("innerHTML")

                    if price.__contains__("M"):
                        realPrice : int = int(float(price.replace("M", ""))*1000000)
                    else:
                        realPrice : int = int(float(price.replace("K", ""))*100000)

                    # Cerrar ficha
                    container = WebDriverWait(driver,1).until(
                        EC.element_to_be_clickable((By.ID, "genericModalContainer"))
                    )

                    close_button = WebDriverWait(container,4).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[aria-label='Close'].close-large.animated.fadeInDown"))
                    )

                    # Hacer clic en el botón de cierre
                    close_button.click()

                    if cells:
                        name = cells[0].text
                        pos = cells[2].text
                        age = cells[3].text
                        club = cells[4].text
                        att = int(cells[5].text)
                        deff = int(cells[6].text)
                        ovr = int(cells[7].text)
                        priceToBuy = int(float(cells[9].text.replace("M", "")) * 1000000)
                        if priceToBuy<= dinero and not club == "'Athletic Bilbao\nCabezueloPro'" :
                            p = Player(name,pos,age,club,att,deff,ovr,priceToBuy,realPrice)
                            listaJugadores.append(p)

            

            # Ordenar primero por 'inflated' en orden ascendente y luego por 'avrMedia' en orden descendente
            listaJugadores.sort(key=lambda x: (x.inflated, -x.avrMedia))
            for x in listaJugadores:
                print(x)
            
            if len(listaJugadores) >=1:
                print(f'El jugador a comprar sería: {listaJugadores[0]}')
            
                botones = checkIfCanSell()

                if len(botones) != 0:


                    #Compramos al jugador 
                    nombreJugador = listaJugadores[0].name
                    #Hacer click y comprar
                    span_element = driver.find_element(By.XPATH, f"//td[.//span[text()='{nombreJugador}']]")

                    span_element.click()


                    btnToShop = WebDriverWait(driver,5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@id='modal-dialog-buyforeignplayer']//button[contains(@class, 'btn-new') and contains(@class, 'btn-success') and contains(@class, 'btn-wide')]"))

                    )

                    # Haz clic en el botón encontrado
                    btnToShop.click()
                    print("Botón encontrado y clic realizado. Compra realizada")


                    selenium_driver.refresh_page()
                    
                    #Lo ponemos a la venta
                    threarThreeSellPlayer = threading.Thread(target=thread_sellPlayer,args=(listaJugadores[0],))
                    # Iniciar el hilo
                    threarThreeSellPlayer.start()
                    # (Opcional) Esperar a que el hilo termine
                    threarThreeSellPlayer.join()
        
        print("Poniendo en espera 30 minutos")
        time.sleep(1800) # 30 minutos
        selenium_driver.refresh_page()






def checkIfCanSell():

    selenium_driver  = SeleniumDriver()
    selenium_driver.load_url("https://en.onlinesoccermanager.com/Transferlist#sell-players")
    selenium_driver.load_cookies()
    selenium_driver.refresh_page()

    driver = selenium_driver.driver
   
    botones = driver.find_elements(By.XPATH, "//button[contains(@class, 'btn-new') and contains(@class, 'btn-wide') and contains(@data-bind, 'showSelectSellPlayerModal')]")
    return botones


def thread_sellPlayer(jugadorParaVender):
    selenium_driver  = SeleniumDriver()
    selenium_driver.load_url("https://en.onlinesoccermanager.com/Transferlist#sell-players")
    selenium_driver.load_cookies()
    selenium_driver.refresh_page()
    driver = selenium_driver.driver

    botones = driver.find_elements(By.XPATH, "//button[contains(@class, 'btn-new') and contains(@class, 'btn-wide') and contains(@data-bind, 'showSelectSellPlayerModal')]")

    for boton in botones:
        boton.click()
        time.sleep(3)
        span_element = driver.find_element(By.XPATH, f"//td[.//span[text()='{jugadorParaVender}']]")
        span_element.click()

        #Drag and drop
        element_to_drag = WebDriverWait(driver, 4).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "slider-handle.min-slider-handle.round"))
        )
        
        time.sleep(1)
        # Crea una instancia de ActionChains
        selenium_driver.actions()
        time.sleep(1)
        selenium_driver.actions.click_and_hold(element_to_drag).move_by_offset(200, 0).release().perform()

        #Confirmar poner en la venta
        a_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'row player-profile-details player-profile-button')]//a[contains(@class, 'btn-new btn-primary btn-wide')]")))
        a_element.click()

        time.sleep(10)





# Crear los hilos
threarOneControlOfCoinsVideos = threading.Thread(target=thread_getCoinsWithVideos)
threarTwoControlOfTransferList = threading.Thread(target=thread_knowBestBuy)



# Iniciar los hilos
threarOneControlOfCoinsVideos.start()
threarTwoControlOfTransferList.start()









#Funciones
def getTimeToSleep(text,driver):
    '''
    En caso de que ya no se pueda reproducir mas videos,
    miramos el tiempo que nos indica, para poder hacer un time.sleep adecuado
    '''
    #elemntContainerText = driver.find_element(By.ID, "modal-dialog-alert")


    
    textoCompleto = text.get_attribute("innerHTML")
    print(textoCompleto)
    numeroEspera : int = 0

    if ("few seconds" or "minuts") in textoCompleto :
        numeroEspera = 120 #2 minutos
    elif "an hour" in textoCompleto:
        numeroEspera = 3600 #1 hora
    else:
        #Encontra

        numeroEspera  = int((re.findall(r'[\d]+',textoCompleto))[0])

        numeroEspera *= 60 

    # Esperar a que el contenedor principal esté presente
    modal_container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "modal-dialog-alert"))
    )

    # Luego, buscar el botón de cierre dentro de este contenedor
    cls_button = WebDriverWait(modal_container, 4).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "close-button-container"))
    )

    # Hacer clic en el botón de cierre
    cls_button.click()
    print("Ventana de información de tiempo de espera cerrada")
    
    return numeroEspera

