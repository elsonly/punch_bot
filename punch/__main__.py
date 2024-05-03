import time
import random
from loguru import logger
import warnings
import datetime as dt

from punch.punch import punch_selenium, check_active
from punch.utils import get_tpe_datetime
from punch.config import CONFIG


def punch_job(debug: bool = False):
    if get_tpe_datetime().weekday() > 4:
        return
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
    from punch.scheduler import Scheduler, Schedule

    scheduler = Scheduler()
    jobs = [
        Schedule(
            name="punch",
            job=punch_job,
            prev_dt=None,
            next_dt=get_tpe_datetime().replace(
                hour=7, minute=30, second=0, microsecond=0
            ),
            interval=dt.timedelta(days=1),
        ),
        Schedule(
            name="punch",
            job=punch_job,
            prev_dt=None,
            next_dt=get_tpe_datetime().replace(
                hour=17, minute=30, second=0, microsecond=0
            ),
            interval=dt.timedelta(days=1),
        ),
    ]
    for schedule in jobs:
        scheduler.register(schedule)

    
    punch_job(debug=True)
    scheduler.run()
