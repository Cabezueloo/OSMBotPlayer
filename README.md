# OSM Bot 🤖⚽

An automation bot for [Online Soccer Manager](https://en.onlinesoccermanager.com/) that handles three tasks in parallel via Selenium:

| Thread | Task |
|--------|------|
| Hilo 1 | Watch video ads to farm coins (BusinessClub page) |
| Hilo 2 | Scan the transfer list, buy undervalued players, then list them for sale |
| Hilo 4 | Manage player training — complete finished sessions, assign new ones before the match window closes |

---

## Requirements

- Python 3.12+
- Google Chrome + matching ChromeDriver (see [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads))
- The ChromeDriver binary must be on your `PATH` **or** placed in the project root

```bash
pip install -r requirements.txt
```

---

## First-Time Setup — Login

The bot authenticates via session cookies. You must log in once to generate them.

### Option A — Manual login (recommended)
```bash
python Login.py
```
A Chrome window opens. Log in to OSM normally. Once you reach the Dashboard the script prints `Completed` and saves `userData/cookieTest.pkl`.

### Option B — Automatic login
```bash
python AutomaticLogin.py
```
Fills in your credentials programmatically. Useful if OSM's login flow is stable.

### Option C — GUI login (full app flow)
```bash
python Inicio.py
```
Opens a small login form. On success it saves your session and launches the Menu.

> ⚠️ **`userData/` is in `.gitignore` and will never be committed.** It contains your session cookies and saved preferences.

---

## Running the Bot

### GUI (recommended)
```bash
python Inicio.py   # first run — logs you in
python Menu.py     # subsequent runs — opens the control panel
```

Use the checkboxes to enable/disable each module and enter your team name + minimum budget before clicking **Start**.

### CLI (headless / scripting)
```bash
python main.py [team_name] [min_budget] [do_coins] [do_trade] [do_training]
```

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `team_name` | str | `"Inter Milan"` | Your team name (used to skip your own players on the market) |
| `min_budget` | int | `10000000` | Minimum funds required before buying |
| `do_coins` | bool | `False` | Enable video-coin thread |
| `do_trade` | bool | `True` | Enable buy-sell thread |
| `do_training` | bool | `False` | Enable training thread |

**Example — enable all three modules:**
```bash
python main.py "My Team" 8000000 True True True
```

Stop anytime with `Ctrl-C`.

---

## How the buy-sell module works

1. Reads your current **club funds** from the top navigation bar.
2. Checks how many **sell slots** are free (max 4).
3. Scans every player in the transfer list and retrieves their **real market value** from the player card.
4. Computes **inflation** = `(buyPrice - realPrice) / realPrice × 100 %`.
5. Sorts candidates: lowest inflation first, then highest average rating.
6. Buys players whose inflation is below `max_inflation` (default **35 %**) — affordability checked serially against a rolling budget.
7. Immediately lists each purchased player for the **maximum price** (slider dragged to the right).

> The bot **will not buy** if funds are below `min_budget` or all 4 sell slots are occupied.

---

## Project structure

```
.
├── main.py             # Core bot threads (coins, trade, training)
├── Menu.py             # PyQt5 GUI control panel
├── Inicio.py           # PyQt5 login / first-run screen
├── Login.py            # Manual cookie capture
├── AutomaticLogin.py   # Programmatic login
├── SeleniumDriver.py   # Chrome driver wrapper + popup handling
├── Player.py           # Player dataclass + sorting logic
├── RutuasAlHTML.py     # All CSS/XPath selectors (centralised)
├── utils.py            # Shared constants (paths, option keys)
├── requirements.txt
└── userData/           # ← gitignored; created at runtime
    ├── cookieTest.pkl  # Session cookies
    ├── credentials_account_file.txt
    └── options_marked.txt
```

---

## Configuration

All HTML selectors are centralised in `RutuasAlHTML.py` — if OSM updates its UI, only that file needs changing.

The inflation threshold and minimum budget can be adjusted:
- **GUI:** via the "Millones" field in `Menu.py`
- **CLI:** via the `min_budget` argument
- **Code:** `max_inflation` parameter in `thread_knowBestBuy()` (default `35.0`)

---

## Disclaimer

This project is for **educational purposes only**. Automating interactions with online games may violate the game's Terms of Service. Use at your own risk.
