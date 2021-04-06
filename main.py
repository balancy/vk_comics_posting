import os
import random

from dotenv import load_dotenv
import requests

COMICS_API_URL = "http://xkcd.com/"
COMICS_FILENAME = "info.0.json"
NUMBER_OF_COMICS = 2450
VK_API_VERSION = "5.130"
VK_API_URL = "https://api.vk.com/method/"


def fetch_comics_info(number):
    response = requests.get(f"{COMICS_API_URL}{number}/{COMICS_FILENAME}")
    response.raise_for_status()

    return response.json()


def download_comics(url, title):
    response = requests.get(url)
    response.raise_for_status()

    with open(f"files/{title}.png", 'wb') as f:
        f.write(response.content)


def get_vk_groups(access_token):
    params = {
        "access_token": access_token,
        "v": VK_API_VERSION,
    }

    response = requests.get(f"{VK_API_URL}groups.get", params=params)
    response.raise_for_status()

    return response.json()


def get_url_to_upload_photo(access_token):
    params = {
        "access_token": access_token,
        "v": VK_API_VERSION,
    }
    response = requests.get(
        f"{VK_API_URL}photos.getWallUploadServer",
        params=params,
    )
    response.raise_for_status()

    return response.json().get("response")


def post_photo_on_server(url_to_upload, filename):
    with open(filename, "rb") as file:
        files = {
            "file1": file,
        }
        response = requests.post(url_to_upload, files=files)
        response.raise_for_status()

    return response.json()


def save_wall_photo(access_token, photo_info):
    params = photo_info.copy()
    params.update({
        "access_token": access_token,
        "v": VK_API_VERSION,
    })

    response = requests.post(f"{VK_API_URL}photos.saveWallPhoto", params=params)
    response.raise_for_status()

    return response.json().get("response")[0]


def post_photo_on_wall(access_token, group_id, comment, image_id, owner_id):
    params = {
        "access_token": access_token,
        "v": VK_API_VERSION,
        "owner_id": -int(group_id),
        "from_group": 1,
        "message": comment,
        "attachments": f"photo{owner_id}_{image_id}"
    }

    response = requests.post(f"{VK_API_URL}wall.post", params=params)
    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    load_dotenv()
    access_token = os.getenv("ACCESS_TOKEN")
    group_id = os.getenv("GROUP_ID")

    comics_number = random.randint(1, NUMBER_OF_COMICS + 1)
    response = fetch_comics_info(comics_number)
    print(response)
    img_url = response.get("img")
    comics_title = response.get("title")
    # comment = response.get("alt")
    # print(comment)

    os.makedirs("files", exist_ok=True)
    download_comics(img_url, comics_title)

    url_to_upload = get_url_to_upload_photo(access_token)
    print(url_to_upload)
    photo_info = post_photo_on_server(url_to_upload.get("upload_url"), f"files/{comics_title}.png")
    print(photo_info)
    isSaved = save_wall_photo(access_token, photo_info)
    print(isSaved)
    is_posted = post_photo_on_wall(
        access_token,
        group_id,
        comics_title,
        isSaved.get("id"),
        isSaved.get("owner_id"),
    )
    print(is_posted)
