import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

AUTHORIZED_USERS = {
    "makoklyuy": "Гоша",
    "sokolovpeter": "Петя",
    "RNFRI": "Артём"
}

BARTENDERS = ["Гоша", "Петя"]
RESERVE_BARTENDER = "Артём"
SCHEDULE_GENERATION_DAY = 25
AUTO_UPDATE_INTERVAL = 12
DATABASE_PATH = "krasin_bar.db"
CALENDAR_IMAGE_PATH = "calendar.jpg"

