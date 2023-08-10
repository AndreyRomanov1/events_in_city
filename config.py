import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

bot_admins = [
    int(os.getenv("ADMIN_ID"))
]

DATABASE_USERNAME = str(os.getenv("DATABASE_USERNAME"))
DATABASE_PASSWORD = str(os.getenv("DATABASE_PASSWORD"))
DATABASE_HOST = str(os.getenv("DATABASE_HOST"))
DATABASE_NAME = str(os.getenv("DATABASE_NAME"))

sql_types = {
    "MYSQL": f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}",
    "sqlite": "sqlite:///db/events_in_city.sqlite?check_same_thread=False"
}
