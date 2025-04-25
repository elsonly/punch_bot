import requests
from loguru import logger
import warnings
from bs4 import BeautifulSoup
import os
import time
import json
import datetime as dt

os.environ["https_proxy"] = "http://128.110.10.186:8080"
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""

from selenium import webdriver
import chromedriver_autoinstaller

from punch.utils import get_tpe_datetime

URL = "http://128.110.13.61/Attendance/Intranet/Attendance/SingleLogin.asp"
HEADER = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Length": "157",
    "Content-Type": "application/x-www-form-urlencoded",
    # "Cookie":"ASPSESSIONIDQQBACBCA=COGOMDKBMHBODJAMFFBEJAOO",
    "Host": "128.110.13.61",
    "Origin": "http://128.110.13.61",
    "Referer": "http://128.110.13.61/Attendance/Intranet/Attendance/SingleLogin.asp",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36",
}


def get_host_time():
    local_dt = get_tpe_datetime()
    dates = local_dt.strftime("%Y/%m/%d")
    hours = str(local_dt.hour)
    minutes = str(local_dt.minute)
    seconds = str(local_dt.second)
    try:
        resp = requests.post(URL, HEADER)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        input_tags = soup.find_all("input")
        for x in input_tags:
            if x.attrs["name"] == "dates":
                dates = x.attrs["value"]
            elif x.attrs["name"] == "hours":
                hours = x.attrs["value"]
            elif x.attrs["name"] == "minutes":
                minutes = x.attrs["value"]
            elif x.attrs["name"] == "seconds":
                seconds = x.attrs["value"]
    except Exception as e:
        logger.exception(e)

    return dates, hours, minutes, seconds


def punch(user_id: str, user_pwd: str, user_name: str) -> bool:
    local_dt = get_tpe_datetime()
    dates, hours, minutes, seconds = get_host_time()
    data = {
        "now": f"1{local_dt.year-2000}/{local_dt.month-1}/{local_dt.day} {local_dt.strftime('%H:%M:%S')}",
        "nowhost": f"{dates} {hours}:{minutes}:{seconds}",
        "txtUserID": user_id,
        "txtUserPwd": user_pwd,
        "dates": dates,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
    }
    logger.info({key: val for key, val in data.items() if key != "txtUserPwd"})
    try:
        resp = requests.post(URL, headers=HEADER, data=data)
        resp.encoding = "utf-8"

        if user_id in resp.text and user_name in resp.text:
            if "刷卡完成" in resp.text:
                return True
        return False

    except Exception as e:
        logger.exception(e)
        return False


def punch_selenium(user_id: str, user_pwd: str) -> bool:
    # chromedriver_autoinstaller.install()
    # options = webdriver.ChromeOptions()
    # options.add_argument("--disable-features=StrictTransportSecurity")
    # options.add_argument("--disable-features=NetworkService")
    # options.add_argument("--allow-running-insecure-content")
    # options.add_argument("--ignore-certificate-errors")
    # options.add_argument("--disable-features=InsecureRedirect")
    # options.add_argument("--disable-features=StrictTransportSecurity")
    # options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # options.add_argument("--disable-web-security")
    # options.add_argument("--disable-extensions")
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')

    # custom User-Agent header
    # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    # driver = webdriver.Chrome(options=options)
    options = webdriver.EdgeOptions()
    driver = webdriver.Edge(executable_path="./dist/msedgedriver.exe", options=options)
    # get
    driver.get(URL)
    time.sleep(3)

    # driver.switch_to.frame("main")
    # time.sleep(3)
    e_user_id = driver.find_element_by_id(id_="txtUserID")
    e_pwd = driver.find_element_by_id(id_="txtUserPwd")
    e_button = driver.find_element_by_tag_name("button")

    e_user_id.send_keys(user_id)
    e_pwd.send_keys(user_pwd)
    e_button.click()
    time.sleep(3)
    result = "刷卡完成" in driver.page_source
    driver.close()
    return result


def check_active() -> bool:
    info = {}
    url = "https://github.com/elsonly/punch_bot/wiki"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        resp = requests.get(url)
    soup = BeautifulSoup(resp.content, features="lxml")
    for x in soup.findAll("p"):
        if "active" in x.text:
            info = json.loads(x.text)
            break

    in_active = info.get("active", False)
    return in_active

    in_date = dt.datetime.fromisoformat(info.get("date", "1900-01-01")).date()

    return in_active and (in_date == get_tpe_datetime().date())
