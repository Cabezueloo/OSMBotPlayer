"""OSM bot entry point — launch bot threads from the command line.

Usage:
    python main.py [team_name] [min_money] [do_coins] [do_trade] [do_train]

Defaults: 'Inter Milan'  25_000_000  True  True  True
"""

import sys
import threading

from bot.videos import thread_getCoinsWithVideos
from bot.trading import thread_knowBestBuy
from bot.training import thread_trainingPlayers

if __name__ == "__main__":
    args = sys.argv[1:]
    own_team  = args[0]       if len(args) > 0 else "Inter Milan"
    min_money = int(args[1])  if len(args) > 1 else 25_000_000
    do_coins  = eval(args[2]) if len(args) > 2 else True
    do_trade  = eval(args[3]) if len(args) > 3 else False
    do_train  = eval(args[4]) if len(args) > 4 else True

    thread_defs = [
        (do_coins, "Hilo 1", thread_getCoinsWithVideos, ()),
        (do_trade, "Hilo 2", thread_knowBestBuy,        (min_money, own_team)),
        (do_train, "Hilo 4", thread_trainingPlayers,    ()),
    ]

    active_threads: list[threading.Thread] = []
    for enabled, name, target, targs in thread_defs:
        if enabled:
            print(f"Iniciando {name} — {target.__name__}")
            t = threading.Thread(target=target, args=targs, name=name, daemon=False)
            t.start()
            active_threads.append(t)

    try:
        for t in active_threads:
            t.join()
    except KeyboardInterrupt:
        print("Bot detenido manualmente.")
