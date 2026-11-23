import os
import requests
from dotenv import load_dotenv

load_dotenv()

EMT_EMAIL = os.getenv("EMT_EMAIL")
EMT_PASSWORD = os.getenv("EMT_PASSWORD")

def get_emt_token():
    if not EMT_EMAIL or not EMT_PASSWORD:
        raise ValueError("Faltan EMT_EMAIL o EMT_PASSWORD en .env")

    response = requests.get(
        "https://openapi.emtmadrid.es/v2/mobilitylabs/user/login/",
        headers={
            "email": EMT_EMAIL,
            "password": EMT_PASSWORD,
        },
        timeout=15,
    )

    response.raise_for_status()
    data = response.json()

    if data.get("code") != "00":
        raise RuntimeError(
            f"Error de autenticación EMT: {data.get('code')}"
        )

    return data["data"][0]["accessToken"]

if __name__ == '__main__':
    print(get_emt_token())