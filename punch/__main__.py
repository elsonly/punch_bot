import time
import random
from loguru import logger
import requests
import json
from bs4 import BeautifulSoup
import warnings
import datetime as dt

from punch.punch import punch_selenium
from punch.utils import get_tpe_datetime
from punch.config import CONFIG


def check_active(url: str):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        resp = requests.get(
            url, proxies={"https": "http://128.110.10.186:8080"}, verify=False
        )

    soup = BeautifulSoup(resp.content, "lxml")
    for meta in soup.find_all("meta", property="og:description"):
        try:
            idx = meta["content"].find("{")
            if idx >= 0:
                data = json.loads(meta["content"][idx:])
                return data["day"] == get_tpe_datetime().day
        except:
            pass
    raise Exception("Cannot find status")


def punch_job(debug: bool = False):
    active = False
    while (
        debug
        or (
            get_tpe_datetime().time() >= dt.time(hour=7, minute=30, second=0)
            and get_tpe_datetime().time() < dt.time(hour=8, minute=25, second=0)
        )
        or (
            get_tpe_datetime().time() >= dt.time(hour=17, minute=30, second=0)
            and get_tpe_datetime().time() < dt.time(hour=19, minute=0, second=0)
        )
    ):
        try:
            active = check_active(CONFIG.HACKMD_PUNCH_URL)
            if active:
                break
        except Exception as e:
            logger.error(e)
        logger.debug("punch not active")
        time.sleep(60)

    if active:
        if not debug:
            time.sleep(random.randint(0, 300))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = punch_selenium(CONFIG.USER_ID, CONFIG.USER_PASSWORD)
        logger.info(f"punch success: {result}")
    else:
        logger.info(f"punch inactive")


if __name__ == "__main__":
    import schedule

    # punch_job(debug=True)
    schedule_time = "07:30:00"
    schedule.every().monday.at(schedule_time).do(punch_job)
    schedule.every().tuesday.at(schedule_time).do(punch_job)
    schedule.every().wednesday.at(schedule_time).do(punch_job)
    schedule.every().thursday.at(schedule_time).do(punch_job)
    schedule.every().friday.at(schedule_time).do(punch_job)

    for _job in schedule.get_jobs():
        logger.info({_job})

    while True:
        schedule.run_pending()
        time.sleep(1)
