# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project overview

Selenium-based automation bot for the web game [Online Soccer Manager](https://en.onlinesoccermanager.com). It automates three activities concurrently using Python threads: watching video ads to earn coins, buying/selling players on the transfer market, and managing player training.

## Setup

Install dependencies into a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Chrome / chromedriver**:
- Linux: chromedriver must be installed at `/usr/bin/chromedriver` (e.g. `sudo apt install chromium-driver`)
- Windows: `chromedriver.exe` is bundled in the project root

The `userData/` directory (gitignored) is created at runtime and stores credentials and session cookies. It must exist before the bot can run:

```bash
mkdir -p userData
```

## Running the bot

**GUI entry point (recommended)**:
```bash
python Inicio.py
```
On first launch this shows a login form; after successful login it transitions to the main menu (`Menu.py`).

**Skip the login screen** (if `userData/credentials_account_file.txt` already exists):
```bash
python Menu.py
```

**Headless / CLI** (no GUI, all features enabled by default):
```bash
python main.py [team_name] [min_money_int] [video_coins_bool] [buy_sell_bool] [training_bool]
# e.g.
python main.py "Athletic Bilbao" 10000000 True True True
```

## Architecture

### Application flow

```
Inicio.py  ──(credentials exist?)──► Menu.py (PyQt5 GUI)
               │                         │
               └─(no)──► login form      └──► main.py threads
                          AutomaticLogin.py
```

`Inicio.py` is the true entry point. It checks for `userData/credentials_account_file.txt`; if missing, it renders a PyQt5 login window that calls `AutomaticLogin.py` to authenticate and save cookies to `userData/cookieTest.pkl`. Once credentials exist, `Menu.py` is launched.

### Thread model (`main.py`)

Four threads run independently; threads are named for debugging via `termcolor`-coloured console output:

| Thread | Name | Color | Purpose |
|--------|------|-------|---------|
| `thread_getCoinsWithVideos` | Hilo 1 | Red | Continuously clicks and waits through video ads on the Business Club page to earn coins |
| `thread_knowBestBuy` | Hilo 2 | Green | Every 30 min: reads the transfer list, scores players by inflation/stats, buys undervalued ones; spawns Hilo 3 |
| `thread_sellPlayer` | Hilo 3 | Blue | Spawned by Hilo 2 after purchases; lists the bought players for sale at maximum price using a slider drag |
| `thread_trainingPlayers` | Hilo 4 | Yellow | Manages training slots: completes finished sessions, adds new players if >7 h before match, watches training ads |

All threads handle wait-message dialogs from OSM (e.g. "come back in X minutes") by parsing the message text in `getTimeToSleep()` and calling `time.sleep()` accordingly.

### Key modules

- **`SeleniumDriver.py`** — Wrapper around `selenium.webdriver.Chrome`. `create(url)` loads the URL, injects saved cookies, refreshes the page, and initialises `ActionChains`. `refresh_page()` also dismisses known OSM pop-up modals (consent dialog, center popup, skill-rating update modal). Platform detection selects the correct chromedriver path automatically.
- **`RutuasAlHTML.py`** — Single source of truth for all CSS/XPath selectors used across the codebase. Any time OSM changes its HTML, only this file needs updating.
- **`Player.py`** — Data class for transfer-market players. Computes `inflated` (price inflation %) and `avrMedia` (average of att/def/ovr). Players are sorted ascending by `inflated`, then descending by `avrMedia` to prioritise cheap, high-quality buys. Only players with `inflated < 35` are actually purchased.
- **`utils.py`** — Path constants (`userData/` files) and option-key string constants shared between `Menu.py` and `main.py`.
- **`AutomaticLogin.py`** — Drives the OSM login form programmatically and dumps session cookies to `userData/cookieTest.pkl` on success.

### Persistent runtime files (all gitignored)

| File | Purpose |
|------|---------|
| `userData/credentials_account_file.txt` | Plain-text username/password; presence is used as a "logged in" flag |
| `userData/cookieTest.pkl` | Pickle of Selenium cookies injected by `SeleniumDriver.load_cookies()` |
| `userData/options_marked.txt` | Last-saved menu settings (Python dict literal); loaded by `Menu.lastOptionsMarked()` |
| `Redirection.txt` | Append-only log of Hilo 1 activity |

### HTML selector strategy

OSM is a Knockout.js SPA. XPath and CSS selectors in `RutuasAlHTML.py` target `data-bind` attributes and stable class names. When selectors break after an OSM update, check that file first — it covers all interactive elements (play buttons, transfer table, training panels, modal close buttons, etc.).
