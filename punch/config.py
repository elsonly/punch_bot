import os
from dotenv import load_dotenv
import datetime as dt

if not os.path.exists(".env"):
    raise Exception("please provide .env")
load_dotenv()


class BaseConfig:
    USER_ID = os.environ.get("USER_ID")
    USER_PASSWORD = os.environ.get("USER_PASSWORD")
    USER_NAME = os.environ.get("USER_NAME")
    HACKMD_PUNCH_URL = os.environ.get("HACKMD_PUNCH_URL")


CONFIG = BaseConfig()
