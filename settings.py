import os

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")
API_TOKEN = os.getenv("API_TOKEN")
BASE_URL = os.getenv("BASE_URL")
# """for debug"""
# API_TOKEN = "yourkey"
# BASE_URL = "https://api.telegram.org/bot"
# REDIS_HOST = "localhost"
# REDIS_PORT = 6379
# REDIS_DB = 0