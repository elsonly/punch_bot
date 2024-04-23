import time
import random
from loguru import logger
import warnings
import datetime as dt

from punch.punch import punch_selenium, check_active
from punch.utils import get_tpe_datetime
from punch.config import CONFIG


def punch_job(debug: bool = False):
    active = False
    while (
        debug
        or (
            get_tpe_datetime().time() >= dt.time(hour=7, minute=30, second=0)
            and get_tpe_datetime().time() < dt.time(hour=10, minute=0, second=0)
        )
        or (
            get_tpe_datetime().time() >= dt.time(hour=17, minute=30, second=0)
            and get_tpe_datetime().time() < dt.time(hour=19, minute=0, second=0)
        )
    ):
        active = check_active()
        if active:
            break
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
    for schedule_time in ["07:30:00", "17:30:00"]:
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
