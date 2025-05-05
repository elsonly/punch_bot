import time
import random
from loguru import logger
import warnings
import datetime as dt

from punch.punch import punch_selenium, check_active
from punch.utils import get_tpe_datetime
from punch.config import CONFIG


def punch_job(debug: bool = False, max_retry: int = 5):
    if get_tpe_datetime().weekday() > 4:
        return
    active = False
    retry_counter = 0
    while (
        debug
        or (
            get_tpe_datetime().time() >= dt.time(hour=7, minute=30, second=0)
            and get_tpe_datetime().time() < dt.time(hour=9, minute=0, second=0)
        )
        or (
            get_tpe_datetime().time() >= dt.time(hour=17, minute=30, second=0)
            and get_tpe_datetime().time() < dt.time(hour=19, minute=0, second=0)
        )
    ):
        try:
            active = check_active()
        except:
            retry_counter += 1
            if retry_counter >= max_retry:
                print("max retries exceeded")
                active = True
        if active:
            break
        logger.debug("punch not active")
        time.sleep(CONFIG.CHECK_INTERVAL)

    if active:
        if not debug:
            interval = int(
                get_tpe_datetime()
                .replace(hour=8, minute=30, second=0, microsecond=0)
                .timestamp()
                - time.time()
            )
            if interval > 0:
                time.sleep(random.randint(0, interval))

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
