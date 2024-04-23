import datetime as dt


def get_tpe_datetime() -> dt.datetime:
    return dt.datetime.utcnow() + dt.timedelta(hours=8)
