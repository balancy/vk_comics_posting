# Comics posting on VK

![comics](https://i.ibb.co/CQ42LwG/comics.png)

Script allows post random xkcd comics on the wall of your group in vkontakte social network.

## How to install
Python3 and Git should be already installed. 

1. Clone the repository by command:
```console
git clone https://github.com/balancy/vk_comics_posting
```
2. Inside cloned repository create virtual environment by command:
```console
python -m venv env
```
3. Activate virtual environment. For linux-based OS:
```console
source env/bin/activate
```
&nbsp;&nbsp;&nbsp;&nbsp;For Windows:
```console
env\scripts\activate
```
4. Install dependencies:
```
pip install -r requirements.txt
```
5. Rename file `.env.example` to `.env` and initialize your proper group_id and access_token:
```console
VK_GROUP_ID=111111111
VK_ACCESS_TOKEN=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```
&nbsp;&nbsp;&nbsp;&nbsp;
where `VK_GROUP_ID` is the id of vkontakte group where you want to post comics

&nbsp;&nbsp;&nbsp;&nbsp;
where `VK_ACCESS_TOKEN` is your authentication token of vkontakte social network

6. Run script by command:
```console
python main.py
```
## Project Goals
The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
