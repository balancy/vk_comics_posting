import functools
import os
import random
import sys

from dotenv import load_dotenv
import requests

COMICS_API_URL = "http://xkcd.com/"
COMICS_FILENAME = "info.0.json"
VK_API_VERSION = "5.130"
VK_API_URL = "https://api.vk.com/method/"


def fetch_comics_info(number):
    """Extracts comics info such as title, author comment, url to image, etc.

    :param number: comics number
    :return: parsed response
    """

    if not number:
        url = f"{COMICS_API_URL}{COMICS_FILENAME}"
    else:
        url = f"{COMICS_API_URL}{number}/{COMICS_FILENAME}"
    response = requests.get(url)
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

    with open(filename, "wb") as f:
        f.write(response.content)


def handle_vk_exceptions(func):
    """Handling vk errors.

    :param func: function to analyse
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if error_elm := result.get("error"):
            raise requests.HTTPError(error_elm.get("error_msg"))
        return result

    return wrapper


@handle_vk_exceptions
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

    return response.json()


@handle_vk_exceptions
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


@handle_vk_exceptions
def save_uploaded_image_on_server(access_token, server, photo, photo_hash):
    """Saves uploaded image on server.

    :param access_token: VK API access token
    :param server: server where uploaded image is keeping
    :param photo: image info
    :param photo_hash: photo's hash
    :return: parsed response
    """

    params= {
        "server": server,
        "photo": photo,
        "hash": photo_hash,
        "access_token": access_token,
        "v": VK_API_VERSION,
    }

    response = requests.post(
        f"{VK_API_URL}photos.saveWallPhoto",
        params=params
    )
    response.raise_for_status()

    return response.json()


@handle_vk_exceptions
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
    access_token = os.getenv("VK_ACCESS_TOKEN")
    group_id = os.getenv("VK_GROUP_ID")

    os.makedirs("files", exist_ok=True)
    filename = "files/comics.png"

    try:
        total_number_of_comics = fetch_comics_info(0).get("num")
        comics_number = random.randint(1, total_number_of_comics)
        comics_info = fetch_comics_info(comics_number)

        comics_img_url = comics_info.get("img")
        comics_title = comics_info.get("title")
        filename = f"files/{comics_title}.png"

        download_comics(comics_img_url, filename)

        url_to_upload = find_url_to_upload_image(access_token)
        photo_info = upload_image_on_server(
            url_to_upload.get("response").get("upload_url"),
            filename,
        )

        saved_image = save_uploaded_image_on_server(
            access_token,
            photo_info.get("server"),
            photo_info.get("photo"),
            photo_info.get("hash"),
        )

        saved_image = saved_image.get("response")[0]
        post_image_on_wall(
            access_token,
            group_id,
            comics_title,
            saved_image.get("id"),
            saved_image.get("owner_id"),
        )
    except requests.HTTPError as e:
        sys.exit(f"Error: {e}. Try later.")
    except requests.ConnectionError as e:
        sys.exit(f"Error: {e}. Try later.")
    finally:
        if os.path.exists(filename):
            os.remove(filename)
