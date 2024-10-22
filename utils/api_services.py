import requests
import os


def get_access_token():
    res = requests.post(url=f"{os.getenv('AUTH_API')}", data={
        "grant_type": "password",
        "client_id": "AEJQhrWaWZCxNMZT3vIYHfVzINSIE3FXdM8H6syU",
        "client_secret": "aiQr79dtPALuhefkIjgfwBw7CMKxuUGgwOQzkymB",
        "username": "robot.soittojarjestelma@honkio.com",
        "password": "d32d3hbvre5654sdfggh"
    })
    return res.json()['access_token']

