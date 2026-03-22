"""XPath and CSS selectors for OSM HTML elements."""

# ---------------------------------------------------------------------------
# Business Club / Video ads
# ---------------------------------------------------------------------------

PLAY_BUTTON_VIDEOS_AD_COINS = "div.business-club-method-container[data-bind*='openWatchVideosModal']"

CONTENIDO_MENSAJE_DE_ESPERA = "//p[@data-bind='html: content']"

# ---------------------------------------------------------------------------
# Transfer list
# ---------------------------------------------------------------------------

TABLA_JUGADORES_EN_VENTA = '//table[contains(@class, "table table-sticky thSortable")]'

FICHA_JUGADOR_AL_HACER_CLICK_EN_LA_TABLA = (
    "//div[@id='genericModalContainer']"
    "//div[@id='modal-dialog-buydomesticplayer' or "
    "@id='modal-dialog-buyforeignplayer' or "
    "@id='modal-dialog-canceltransferplayer']"
)

PRECIO_REAL_JUGADOR_DESDE_LA_FICHA_ABIERTA = ".//div[@class='player-profile-value']/span[2]"

BOTON_CERRAR_FICHA_JUGADOR_TABLA = "div[aria-label='Close'].close-large.animated.fadeInDown"

BOTON_CONFIRMAR_PONER_A_LA_VENTA = (
    "//div[contains(@class, 'row player-card-menu center slide-out-bottom-animation')]"
    "//a[contains(@class, 'btn-new btn-primary btn-wide')]"
)

# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

BOTON_VER_ANUNCIO_JUGADORES_ENTRENANDO = (
    "//div[contains(@class, 'training-panel-footer center')]"
    "//button[contains(@class, 'btn-new center')]"
)

BOTON_COMPLETE_DE_LOS_ENTRENAMIENTOS = (
    "//button[contains(@class, 'btn-new btn-success btn-show-result')]"
    "//span[contains(text(), 'Complete')]"
)

BOTON_START_PONER_JUGADOR_A_ENTRENAR = (
    "//button[contains(@class, 'btn-new btn-primary')]"
    "//span[contains(text(), 'Start')]"
)

BOTON_OK_MENSAJE_CONFIRMACION_PONER_JUGADOR_A_ENTRENAR = (
    "//div[@id='modal-dialog-confirm']//div[@data-bind='click: okAction']"
)
