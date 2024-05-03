from loguru import logger
import time
import datetime as dt
from typing import TypedDict, Callable, List

from punch.utils import get_tpe_datetime


class Schedule(TypedDict):
    name: str
    job: Callable
    prev_dt: dt.datetime
    next_dt: dt.datetime
    interval: dt.timedelta


class Scheduler:
    def __init__(self):
        self.__active_schedule = False
        self.schedules: List[Schedule] = []

    def register(self, schedule: Schedule):
        logger.info(f"register job: {schedule}")
        self.schedules.append(schedule)

    def run(self):
        self.__active_schedule = True
        while self.__active_schedule:
            cur_dt = get_tpe_datetime()
            for schedule in self.schedules:
                if cur_dt >= schedule["next_dt"]:
                    try:
                        schedule["job"]()
                    except Exception as e:
                        logger.exception(e)

                    schedule["prev_dt"] = schedule["next_dt"]
                    schedule["next_dt"] += schedule["interval"]

            time.sleep(1)
