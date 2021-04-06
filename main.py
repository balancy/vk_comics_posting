import os
import random
import sys

from dotenv import load_dotenv
import requests

COMICS_API_URL = "http://xkcd.com/"
COMICS_FILENAME = "info.0.json"
NUMBER_OF_COMICS = 2450
VK_API_VERSION = "5.130"
VK_API_URL = "https://api.vk.com/method/"


def fetch_comics_info(number):
    """Extracts comics info such as title, author comment, url to image, etc.

    :param number: comics number
    :return: parsed response
    """

    response = requests.get(f"{COMICS_API_URL}{number}/{COMICS_FILENAME}")
    response.raise_for_status()

    return response.json()


def download_comics(url, filename):
    """Downloads comics locally.

    :param url: utl to comics
    :param filename: name of file to save image to
    :return: None
    """

    response = requests.get(url)
    response.raise_for_status()

    with open(filename, 'wb') as f:
        f.write(response.content)


def find_url_to_upload_image(access_token):
    """Finds url where to upload comics image.

    :param access_token: VK API access token
    :return: parsed response
    """

    params = {
        "access_token": access_token,
        "v": VK_API_VERSION,
    }
    response = requests.post(
        f"{VK_API_URL}photos.getWallUploadServer",
        params=params,
    )
    response.raise_for_status()

    return response.json().get("response")


def upload_image_on_server(url_to_upload, filename):
    """Posts image on VK server.

    :param url_to_upload: url of server
    :param filename: path to the image to upload
    :return: parsed response
    """

    with open(filename, "rb") as file:
        files = {
            "file1": file,
        }
        response = requests.post(url_to_upload, files=files)
        response.raise_for_status()

    return response.json()


def save_uploaded_image_on_server(access_token, image_info):
    """Saves uploaded image on server.

    :param access_token: VK API access token
    :param image_info: information about image
    :return: parsed response
    """

    params = image_info.copy()
    params.update({
        "access_token": access_token,
        "v": VK_API_VERSION,
    })

    response = requests.post(
        f"{VK_API_URL}photos.saveWallPhoto",
        params=params
    )
    response.raise_for_status()

    return response.json().get("response")[0]


def post_image_on_wall(access_token, group_id, title, image_id, owner_id):
    """Posts saved image on group's wall.

    :param access_token: VK API access token
    :param group_id: id of group
    :param title: comics title
    :param image_id: id of image
    :param owner_id: id of image's owner
    :return: parsed response
    """

    params = {
        "access_token": access_token,
        "v": VK_API_VERSION,
        "owner_id": -int(group_id),
        "from_group": 1,
        "message": title,
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
    try:
        comics_info = fetch_comics_info(comics_number)
    except requests.HTTPError:
        print("Unable to reach comics API. Try later")
        sys.exit()

    img_url = comics_info.get("img")
    comics_title = comics_info.get("title")

    os.makedirs("files", exist_ok=True)
    filename = f"files/{comics_title}.png"
    try:
        download_comics(img_url, filename)
    except requests.HTTPError:
        print("Unable to download comics. Try later.")
        sys.exit()

    try:
        url_to_upload = find_url_to_upload_image(access_token)
    except requests.HTTPError:
        print("Unable to find an url to upload comics to. Try later.")
        sys.exit()

    try:
        photo_info = upload_image_on_server(
            url_to_upload.get("upload_url"),
            f"files/{comics_title}.png",
        )
    except requests.HTTPError:
        print("Unable to upload an image on server. Try later.")
        sys.exit()

    try:
        saved_image = save_uploaded_image_on_server(access_token, photo_info)
    except requests.HTTPError:
        print("Unable to save uploaded image on server. Try later.")
        sys.exit()

    try:
        post_image_on_wall(
            access_token,
            group_id,
            comics_title,
            saved_image.get("id"),
            saved_image.get("owner_id"),
        )
    except requests.HTTPError:
        print("Unable to post image on group's wall. Try later.")
        sys.exit()

    os.remove(filename)
