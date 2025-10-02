from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

import requests
import time
import datetime
import random

from threading import Thread


ENABLED = True
TARGET = "Class 2B Practical Test"
GECKO_PATH = "/snap/bin/firefox.geckodriver"  # https://stackoverflow.com/a/78343391


class CDC2BChecker:

    def __init__(self, target, token, chat_id):
        self.token = token
        self.chat_id = chat_id

    def loop(self):
        if not ENABLED:
            return

        # print(datetime.datetime.now(), "Checking...")

        options = Options()
        options.add_argument("--headless")

        service = Service(executable_path=GECKO_PATH)

        driver = webdriver.Firefox(options=options, service=service)
        driver.implicitly_wait(30)

        driver.get("https://www.cdc.com.sg/test-date/")
        elem = driver.find_element(By.XPATH, f"//td[text()='{TARGET}']")
        next_elem = elem.find_element(By.XPATH, "following-sibling::td[1]")

        if "please" not in next_elem.text.lower():
            url = "https://api.telegram.org/bot{}/sendMessage?text={}&chat_id={}"
            res = requests.get(
                url.format(self.token, f"{TARGET} {next_elem.text}", self.chat_id)
            )
            res.raise_for_status()

        driver.quit()

        time.sleep(60 * 5 + random.randint(5, 10))  # 5 min

    def start(self):
        # invoke endless thread
        Thread(target=self.loop).start()


def start(secrets):
    token, chat_id = secrets["telegram"]["token"], secrets["telegram"]["chat_id"]
    CDC2BChecker(token, chat_id).start()


def main():
    c = CDC2BChecker("", "", "")
    c.loop()


if __name__ == "__main__":
    main()
