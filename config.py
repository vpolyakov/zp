import os

from dotenv import load_dotenv

load_dotenv()

LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY')
APP_ID = os.getenv('APP_ID')

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')


def update_token():
    global ACCESS_TOKEN, REFRESH_TOKEN
    load_dotenv()
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')


JOBS_FILE = 'settings/jobs.csv'
