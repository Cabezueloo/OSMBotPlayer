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
from termcolor import colored 
from datetime import datetime

#RED Threard 1
#GREEN Threard 2
#BLUE Threard 3


def thread_getCoinsWithVideos():

    '''Hilo encargado de ver videos siempre que se pueda para recopilar monedas'''
    
    selenium_driver_get_coins  = SeleniumDriver()
    selenium_driver_get_coins.load_url("https://en.onlinesoccermanager.com/BusinessClub")
    selenium_driver_get_coins.load_cookies()
    selenium_driver_get_coins.refresh_page()

    driver = selenium_driver_get_coins.driver
    

    while True:
        try:

            WebDriverWait(driver, 10).until(EC.invisibility_of_element((By.CLASS_NAME, "fc-dialog-overlay")))

            # Esperar hasta que el elemento que reproduce el video sea clickeable
            play_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".row.row-h-xs-150.row-h-sm-24.business-club-method-container.method-container-small.center.watchvideo-method"))
            )

            # Hacer clic en el elemento para reproducir el video
            play_button.click()
            print(colored(f"{threading.current_thread().name}-> Click hecho en el elemento que contiene el video.","red"))

            # Esperar un corto período de tiempo y verificar el estado del video
            time.sleep(5)  # Ajusta este tiempo según la duración de tu espera
            
            # Guardamos el div del video
            video_ad = driver.find_element(By.ID, "videoad")
            videoMostrado = False

            ## Comprobar el estado del div
            while video_ad.is_displayed():
                print(colored(f"{threading.current_thread().name}->El video no ha terminado","red"))
                videoMostrado = True
                time.sleep(15)
              

            #Comprobamos si nos ha dado mensaje de tiempo de espera para ver mas videos
            if not videoMostrado:
                print(colored(f"{threading.current_thread().name}->Video no mostrado, mensaje de espera mostrado, coger tiempo a esperar","red"))
                try:
                    text = driver.find_element(By.XPATH, "//p[@data-bind='html: content']")
                    timeToSleep = getTimeToSleep(text,driver)

                    print(colored(f"{threading.current_thread().name}-> Poniendo en espera {timeToSleep//60} minutos, hora actual es {datetime.now().strftime('%H:%M:%S')}","red"))
                
                    time.sleep(timeToSleep)
                    driver.refresh()

                except Exception:
                    pass

        except Exception as e:
            print(colored(f"{threading.current_thread().name}-> Error{e}","red"))
            break

def thread_knowBestBuy():
    selenium_driver_best_buy  = SeleniumDriver()
    selenium_driver_best_buy.load_url("https://en.onlinesoccermanager.com/Transferlist/")
    selenium_driver_best_buy.load_cookies()
    selenium_driver_best_buy.refresh_page()
    selenium_driver_best_buy.actions()

    
    while True:
        driver = selenium_driver_best_buy.driver
        #Dinero en la cuenta
        span_element = driver.find_element(By.CSS_SELECTOR, 
            'span[data-bind="currency: $parent.shouldShowSavings() ? $parent.savings() : animatedProgress(), roundCurrency: RoundCurrency.Downwards, fractionDigitsK: 1, fractionDigits: 1"]')
        dinero = int(float(span_element.get_attribute("innerHTML").replace("M", "")) * 1000000)
        
        print(colored(f'{threading.current_thread().name}-> Dinero que tengo es de:{dinero} ',"green"))

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
                    #TODO Arreglar el click
                    

                    selenium_driver_best_buy.actions.move_to_element(cells[0]).perform()

                    cells[0].click()
                    
                   # Selecciona el segundo span dentro del div con clase player-profile-value
                    
                    divPadre = driver.find_element(By.XPATH, "//div[@id='genericModalContainer']//div[@id='modal-dialog-buydomesticplayer' or @id='modal-dialog-buyforeignplayer' or @id='modal-dialog-canceltransferplayer']")


                    if divPadre.get_attribute("id") != "modal-dialog-canceltransferplayer":
                        span_element = divPadre.find_element(By.XPATH, ".//div[@class='player-inner-border']//div[@class='player-profile-player']//div[@class='player-profile-value']/span[2]")
                        price :str = span_element.get_attribute("innerHTML")
                        
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
                        if priceToBuy<= dinero and not "Athletic Bilbao" in club :
                            p = Player(name,pos,age,club,att,deff,ovr,priceToBuy,realPrice)
                            listaJugadores.append(p)

            

            # Ordenar primero por 'inflated' en orden ascendente y luego por 'avrMedia' en orden descendente
            listaJugadores.sort(key=lambda x: (x.inflated, -x.avrMedia))
            for x in listaJugadores:
                print(colored(x,"green"))
            
            if len(listaJugadores) >=1:
                print(colored(f'{threading.current_thread().name}->Jugadores disponibles para comprar en base al dinero actual',"green"))
            
                botones = checkIfCanSell()

                print(colored(f'{threading.current_thread().name}-> Hay {botones} huecos para poner jugadores a la venta',"green"))
                
                if botones != 0:

                    jugadoresParaComprar = []

                    #Checkear cuantos compramos.
                    for x in range(botones):
                        if dinero>= listaJugadores[x].priceToBuy:
                            dinero = dinero - listaJugadores[x].priceToBuy
                            jugadoresParaComprar.append(listaJugadores[x].name)
                        else:
                            break #Si no llega el dinero, no hace falta comprobar todos, sabemos que no llegara
                                   


                    #Compramos al jugador/s

                    for jugadorNombre in jugadoresParaComprar:

                        #Hacer click y comprar
                        span_element = driver.find_element(By.XPATH, f"//td[.//span[text()='{jugadorNombre}']]")

                        span_element.click()


                        btnToShop = WebDriverWait(driver,5).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[@id='modal-dialog-buyforeignplayer']//button[contains(@class, 'btn-new') and contains(@class, 'btn-success') and contains(@class, 'btn-wide')]"))

                        )

                        # Haz clic en el botón de comprar
                        btnToShop.click()
                        print(colored(f"{threading.current_thread().name}-> Botón encontrado y clic realizado. Compra realizada del jugador {jugadorNombre}","green"))
                        time.sleep(1)

                        #Refrescamos la pagina en cada compra(cada click)
                        selenium_driver_best_buy.refresh_page()
                    
                    #Los ponemos a la venta
                    threarThreeSellPlayer = threading.Thread(target=thread_sellPlayer,args=(jugadoresParaComprar,),name="Hilo 3")
                            # Iniciar el hilo
                    threarThreeSellPlayer.start()
                    # (Opcional) Esperar a que el hilo termine
                    threarThreeSellPlayer.join()
        
        print(colored(f"{threading.current_thread().name}-> Poniendo en espera 30 minutos, hora actual es {datetime.now().strftime('%H:%M:%S')} ","green"))
        time.sleep(1800) # 30 minutos
        selenium_driver_best_buy.refresh_page()




def checkIfCanSell():

    selenium_driver_check  = SeleniumDriver()
    selenium_driver_check.load_url("https://en.onlinesoccermanager.com/Transferlist#sell-players")
    selenium_driver_check.load_cookies()
    selenium_driver_check.refresh_page()

    driver = selenium_driver_check.driver
   
    botones = driver.find_elements(By.XPATH, "//button[contains(@class, 'btn-new') and contains(@class, 'btn-wide') and contains(@data-bind, 'showSelectSellPlayerModal')]")
    selenium_driver_check.close()
    time.sleep(1)
    return len(botones)


def thread_sellPlayer(jugadoresParaVender):
    selenium_driver_sellPlayer= SeleniumDriver()
    selenium_driver_sellPlayer.load_url("https://en.onlinesoccermanager.com/Transferlist#sell-players")
    selenium_driver_sellPlayer.load_cookies()
    selenium_driver_sellPlayer.refresh_page()
    driver = selenium_driver_sellPlayer.driver

    # Crea una instancia de ActionChains
    selenium_driver_sellPlayer.actions()
    
    botones = driver.find_elements(By.XPATH, "//button[contains(@class, 'btn-new') and contains(@class, 'btn-wide') and contains(@data-bind, 'showSelectSellPlayerModal')]")



    for indice, jugadorAVender in enumerate(jugadoresParaVender):
        
        botones[indice].click()
        time.sleep(3)
        span_element = driver.find_element(By.XPATH, f"//td[.//span[text()='{jugadorAVender}']]")
        span_element.click()

        #Drag and drop para poner el precio maximo
        element_to_drag = WebDriverWait(driver, 4).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "slider-handle.min-slider-handle.round"))
        )
        
        time.sleep(1)
        
        selenium_driver_sellPlayer.actions.click_and_hold(element_to_drag).move_by_offset(200, 0).release().perform()

        #Confirmar poner en la venta
        a_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'row player-profile-details player-profile-button')]//a[contains(@class, 'btn-new btn-primary btn-wide')]")))
        a_element.click()

        print(colored(f'{threading.current_thread().name}-> El jugador, {jugadorAVender} se ha puesto en venta',"blue"))
        selenium_driver_sellPlayer.refresh_page() #Para evitar errores, refrescamos la pagina


if __name__ == "__main__":
    # Crear los hilos
    threarOneControlOfCoinsVideos = threading.Thread(target=thread_getCoinsWithVideos,name="Hilo 1")
    threarTwoControlOfTransferList = threading.Thread(target=thread_knowBestBuy, name="Hilo 2")

    # Iniciar los hilos
    threarOneControlOfCoinsVideos.start()
    threarTwoControlOfTransferList.start()


#Funciones
def getTimeToSleep(text, driver):
    '''
    En caso de que ya no se pueda reproducir más videos,
    miramos el tiempo que nos indica, para poder hacer un time.sleep adecuado
    '''
    textoCompleto = text.get_attribute("innerHTML")
    print(colored(f'{threading.current_thread().name}-> {textoCompleto}', "red"))
    numeroEspera: int = 0

    if ("few seconds" or "minute") in textoCompleto:
        numeroEspera = 120  # 2 minutos
    elif "an hour" in textoCompleto:
        numeroEspera = 3600  # 1 hora
    else:
        numeroEspera = int((re.findall(r'[\d]+', textoCompleto))[0])
        numeroEspera *= 60

    # Esperar y cerrar el modal de overlay si existe
    try:
        overlay = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-shadow"))
        )
        close_button = driver.find_element(By.CLASS_NAME, "close-button-container")
        close_button.click()
        print(colored(f"{threading.current_thread().name}-> Modal cerrado", "red"))
    except Exception as e:
        print(colored(f"{threading.current_thread().name}-> No se encontró el overlay: {e}", "yellow"))

    return numeroEspera

