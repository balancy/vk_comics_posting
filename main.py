import os

import requests

API_URL = "http://xkcd.com/"
FILENAME = "info.0.json"


def fetch_comics_info(number):
    response = requests.get(f"{API_URL}{number}/{FILENAME}")
    response.raise_for_status()

    return response.json()


def download_comics(url, title):
    response = requests.get(url)
    response.raise_for_status()

    with open(f"files/{title}.png", 'wb') as f:
        f.write(response.content)


if __name__ == "__main__":
    comics_number = 614
    response = fetch_comics_info(comics_number)
    img_url = response.get("img")
    title = response.get("title")

    os.makedirs("files", exist_ok=True)
    download_comics(img_url, title)
