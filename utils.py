"""Shared constants for the OSM bot."""

from pathlib import Path

_DATA = Path("userData")

CREDENTIALS_ACCOUNT_FILE: Path = _DATA / "credentials_account_file.txt"
COOKIE_USER_ACCOUNT: Path     = _DATA / "cookieTest.pkl"
OPTIONS_MENU: Path             = _DATA / "options_marked.txt"
REDIRECTION: Path              = Path("Redirection.txt")

# Options-menu dict keys
NAME_TEAM        = "name_team"
MIN_MONEY        = "min_money"
VIDEO_COINS      = "video_coins"
TRADING          = "traiding"
TRAINING_PLAYERS = "training_players"