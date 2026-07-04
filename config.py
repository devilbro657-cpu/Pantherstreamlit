# Default Configuration (Database থেকে override হবে)
API_BASE_URL = "https://games.accbazaar.shop"
API_KEY = "panthers_ySfegn1vdco_lf9chq_-KbG7YAe0YyZMlAadcQ"

# Available Apps
AVAILABLE_APPS = [
    "567slot_game", "Yono_vip", "mbmbet_game", "yonoslot_game",
    "789jackpot_game", "okrummy_game", "Yono777_game", "toprummy_game",
    "Yonogame_game", "spincrush_game", "hirummy_game", "indslot_game",
    "maha_game", "Spin777_game", "Hindi777_game", "Bingo_game",
    "jaiho777_game", "jaiho91_game", "Rummyludo_game", "Shareslots_game",
    "SpinLucky_game"
]

APP_PRICES = {app: 3.0 for app in AVAILABLE_APPS}

# OTP Settings
OTP_SEND_DELAY = 2  # seconds between OTPs

# Database
DB_PATH = "panther.db"
