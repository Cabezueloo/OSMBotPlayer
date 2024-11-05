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
import random
import math

#RED Threard 1
#GREEN Threard 2
#BLUE Threard 3
#YELLOW Threard 3


def thread_getCoinsWithVideos():

    '''Hilo encargado de ver videos siempre que se pueda para recopilar monedas'''
    
    selenium_driver_get_coins  = SeleniumDriver()
    selenium_driver_get_coins.load_url("https://en.onlinesoccermanager.com/BusinessClub")
    selenium_driver_get_coins.load_cookies()
    selenium_driver_get_coins.refresh_page()

    driver = selenium_driver_get_coins.driver
    selenium_driver_get_coins.actions()

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
                print(colored(f"{threading.current_thread().name}->Video no mostrado al intentar ver videos para conseguir monedas, mensaje de espera mostrado , coger tiempo a esperar","red"))
                try:
                    text = driver.find_element(By.XPATH, "//p[@data-bind='html: content']")
                    timeToSleep = getTimeToSleep(text,driver,selenium_driver_get_coins.actions,color = "red")

                    print(colored(f"{threading.current_thread().name}-> Poniendo en espera {timeToSleep//60} minutos el apartado de ver videos para monedas. Hora actual es {datetime.now().strftime('%H:%M:%S')}","red"))
                
                    time.sleep(timeToSleep)
                     

                except Exception:
                    driver.refresh()

        except Exception as e:
            print(colored(f"{threading.current_thread().name}-> Error{e}","red"))
            driver.refresh()


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
        
        botonesDisponibles = checkIfCanSell(driver)

        if dinero>10000000 and botonesDisponibles!= 0:
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
            break

            if len(listaJugadores) >=1:
                print(colored(f'{threading.current_thread().name}->Jugadores disponibles para comprar en base al dinero actual',"green"))
            
                
                jugadoresParaComprar = []

                #Checkear los jugadores que compraremos
                for x in range(botonesDisponibles):
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
                    #selenium_driver_best_buy.refresh_page()
                
                if len(jugadoresParaComprar)>=1:
                    #Los ponemos a la venta
                    threadThreeSellPlayer = threading.Thread(target=thread_sellPlayer,args=(jugadoresParaComprar,),name="Hilo 3")
                    
                    # Iniciar el hilo
                    threadThreeSellPlayer.start()
                    #Esperar a que el hilo termine
                    threadThreeSellPlayer.join()
        
        if dinero<10000000 or botonesDisponibles==0:
            info = "Dinero insuficiente" if dinero<10000000 else "No hay huecos de venta disponible 4/4 ocupado"
            print(colored(f'{threading.current_thread().name}-> {info}',"green"))

        print(colored(f"{threading.current_thread().name}-> Poniendo en espera 30 minutos, hora actual es {datetime.now().strftime('%H:%M:%S')} ","green"))
        time.sleep(1800) # 30 minutos
        selenium_driver_best_buy.refresh_page()




def checkIfCanSell(driver) -> int:
                    
    time.sleep(1)
    sellPlayerText : str = driver.find_element(By.XPATH, "//li[@id='sell-players-tab']//span").text

    numero = re.search(r'\d', sellPlayerText)
    n = int(numero.group())

    return 4- n
   
 

def thread_sellPlayer(jugadoresParaVender):
    selenium_driver_sellPlayer= SeleniumDriver()
    selenium_driver_sellPlayer.load_url("https://en.onlinesoccermanager.com/Transferlist#sell-players")
    selenium_driver_sellPlayer.load_cookies()
    selenium_driver_sellPlayer.refresh_page()
    driver = selenium_driver_sellPlayer.driver

    # Crea una instancia de ActionChains
    selenium_driver_sellPlayer.actions()
    
    botonesDisponibles = driver.find_elements(By.XPATH, "//button[contains(@class, 'btn-new') and contains(@class, 'btn-wide') and contains(@data-bind, 'showSelectSellPlayerModal')]")



    for indice, jugadorAVender in enumerate(jugadoresParaVender):
        
        botonesDisponibles[indice].click()
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
        time.sleep(3)
        #selenium_driver_sellPlayer.refresh_page() #Para evitar errores, refrescamos la pagina


def thread_trainingPlayers():

    selenium_driver_training_players  = SeleniumDriver()
    selenium_driver_training_players.load_url("https://en.onlinesoccermanager.com/Training")
    selenium_driver_training_players.load_cookies()
    while True:
        selenium_driver_training_players.refresh_page()

        driver = selenium_driver_training_players.driver
        
        #Check if a training is completed
        try:
            btn_complete = driver.find_elements(By.XPATH, "//button[contains(@class, 'btn-new btn-success btn-show-result')]//span[contains(text(), 'Complete')]")

            for button in btn_complete:
                button.click()
                time.sleep(2)
            
            time.sleep(15)
                

        except Exception:
            pass


        #Add a player to train
        try:
            btn_add_player_to_train = driver.find_elements(By.XPATH, "//button[contains(@class, 'btn-new btn-primary btn-orange')]//span[contains(text(), 'Start')]")

            #Para que no ponga a 
            tiempoActual = datetime.now().time()
            tiempoDelPartido = datetime.strptime('20::20::00','%H::%M::%S').time()
            diferenciaHora = abs(tiempoDelPartido.hour - tiempoActual.hour)
            diferenciaMinuto= abs(tiempoDelPartido.minute - tiempoActual.minute)

            
            print(colored(f"{threading.current_thread().name}->Tiempo hasta el partido {diferenciaHora} horas y {diferenciaMinuto} minutos ","yellow"))

            if diferenciaHora >8:

                for button in btn_add_player_to_train:
                    button.click()
                    time.sleep(1)
                    listPlayerToClick = driver.find_elements(By.XPATH, "//table[contains(@id, 'squad-table')]//tr")
                    posicion = random.randint(0, 3)
                    posicion = 0
                    listPlayerToClick[posicion+1].click()
                    time.sleep(1)
                    try:
                        btn_ok_action = driver.find_element(By.XPATH, "//div[@id='modal-dialog-confirm']//div[@data-bind='click: okAction']")
                        btn_ok_action.click()
                        time.sleep(5)
                    except Exception:
                        print("El model de confirmar no esta presente.")
            elif len(btn_add_player_to_train)==4:
                print(colored(f"{threading.current_thread().name}->Pausado, ya que no hay entrenamientos haciendose actualmente, no se puede ver videos entonces","yellow"))
                tiempoEspera = (diferenciaHora*3600)+(diferenciaMinuto*60)
                time.sleep(tiempoEspera)
            else:
                print(colored(f"{threading.current_thread().name}->La diferencia del partido es menor que 8, entonces no va a añadir ningun jugador a entrenar","yellow"))

                
        except Exception:
            pass

        #Watch adds in training
        try:
            print(colored(f"{threading.current_thread().name}->Entro para ver si puede hay para pulsar anuncio. hora -> {datetime.now().strftime('%H:%M:%S')}","yellow"))

            btn_watchAd = driver.find_elements(By.XPATH, "//div[contains(@class, 'training-panel-footer center')]//button[contains(@class, 'btn-new center')]")

        
            for index, boton in enumerate(btn_watchAd):
                boton.click()

                print(colored(f"{threading.current_thread().name}-> Click hecho en el boton numero {index}","yellow"))

                # Esperar un corto período de tiempo y verificar el estado del video
                time.sleep(5)  # Ajusta este tiempo según la duración de tu espera
                
                # Guardamos el div del video
                video_ad = driver.find_element(By.ID, "videoad")
                videoMostrado = False

                ## Comprobar el estado del div
                while video_ad.is_displayed():
                    print(colored(f"{threading.current_thread().name}->El video no ha terminado","yellow"))
                    videoMostrado = True
                    time.sleep(15)

                    #Comprobamos si nos ha dado mensaje de tiempo de espera para ver mas videos
                if not videoMostrado:
                    print(colored(f"{threading.current_thread().name}->Video no mostrado al pulsar el boton {index}, mensaje de espera mostrado, coger tiempo a esperar","yellow"))
                    try:
                        text = driver.find_element(By.XPATH, "//p[@data-bind='html: content']")
                        timeToSleep = getTimeToSleep(text,driver,selenium_driver_training_players.actions,color="yellow")

                        print(colored(f"{threading.current_thread().name}-> Poniendo en espera la parte de el entrenamiento de jugador por no poder ver mas videos {timeToSleep//60} minutos, hora actual es {datetime.now().strftime('%H:%M:%S')}","yellow"))
                    
                        time.sleep(timeToSleep)
                    except Exception:
                        break


        except Exception:
            pass

        



if __name__ == "__main__":
    # Crear los hilos
    threadOneControlOfCoinsVideos = threading.Thread(target=thread_getCoinsWithVideos,name="Hilo 1")
    threadTwoControlOfTransferList = threading.Thread(target=thread_knowBestBuy, name="Hilo 2")
    #HILO PONE EN VENTA A LOS JUGADORES COMPRADOS DEL HILO DOS, SE CREA DESDE EL HILO 2

    threadFourControlOfTrainingPlayers = threading.Thread(target=thread_trainingPlayers, name="Hilo 4")


    # Iniciar los hilos
    threadOneControlOfCoinsVideos.start()
    threadTwoControlOfTransferList.start()
    threadFourControlOfTrainingPlayers.start()


#Funciones
def getTimeToSleep(text, driver,actions,color):
    '''
    En caso de que ya no se pueda reproducir más videos,
    miramos el tiempo que nos indica, para poder hacer un time.sleep adecuado
    '''
    textoCompleto = text.get_attribute("innerHTML")
    print(colored(f'{threading.current_thread().name}-> {textoCompleto}', color))
    numeroEspera: int = 0

    if ("few seconds" or "minute") in textoCompleto:
        numeroEspera = 120  # 2 minutos
    elif "an hour" in textoCompleto:
        numeroEspera = 300  # Ponemos 5 minutos para que vuelva a pulsar el boton y coja 45 minutos, ya que no es una hora
    elif "hours" in textoCompleto:
        numeroEspera = 3600 # Ponemos una hora
    else:
        numeroEspera = int((re.findall(r'[\d]+', textoCompleto))[0])
        numeroEspera *= 60

    # Esperar y cerrar el la ventana de información
    try:

        close_button = driver.find_element(By.XPATH, "//div[contains(@id, 'modal-dialog-alert')]//button[contains(@class, 'close')]")

        #actions.move_to_element(close_button).perform()
        close_button.click()
        print(colored(f"{threading.current_thread().name}-> Ventana de información de tiempo a esperar, cerrada", color))
    except Exception as e:
        print(colored(f"{threading.current_thread().name}-> No se encontró el elemento close button de la ventana de informacion: {e}", color))

    return numeroEspera

