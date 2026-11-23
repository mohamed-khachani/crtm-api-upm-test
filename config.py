
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

EMT_EMAIL = os.getenv("EMT_EMAIL")
EMT_PASSWORD = os.getenv("EMT_PASSWORD")

EMT_LOGIN_URL = (
    "https://openapi.emtmadrid.es/v2/"
    "mobilitylabs/user/login/"
)

GTFS_PATH = BASE_DIR / "data" / "crtm.zip"

TIMEZONE = ZoneInfo("Europe/Madrid")

LINES = {
    "566", "571", "573",
    "591", "865", "N905", "ML3"
}

CANDIDATE_STOP_IDS = {
    "17572", "17573",
    "17574", "17575",
    "08411", "08758", "18271"
}

STOP_KEYWORDS = (
    "INFORMAT",
    "MONTEPRINCIPE",
    "MONTEGANCEDO",
    "BADAJOZ",
    "SERVICIOS CENTRALES"
)
