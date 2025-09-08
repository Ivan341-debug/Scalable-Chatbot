import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get('DB_NAME')
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
RABBIT_HOST = os.environ.get('RABBIT_HOST')
RABBIT_USER = os.environ.get('RABBIT_USER')
RABBIT_PASS = os.environ.get('RABBIT_PASS')