from selenium import webdriver

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

import requests
import time
import traceback
import datetime
import random

from threading import Thread


ENABLED = False
TARGET = "Class 2B Practical Test"


class CDC2BChecker:
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id

    def _loop(self):
        while True:
            if not ENABLED:
                return

            try:
                print(datetime.datetime.now(), "Initializing...")

                options = Options()
                options.add_argument("--headless")
                driver = webdriver.Firefox(
                    options=options,
                    executable_path="/home/pi/home-automation/remote/cdc/gecko/geckodriver",
                    service_log_path="/home/pi/home-automation/remote/cdc/gecko/log.log",
                )
                driver.implicitly_wait(30)

                print(datetime.datetime.now(), "Checking Class 2B...")

                driver.get("https://www.cdc.com.sg/test-date/")

                elem = driver.find_element(By.XPATH, f"//td[text()='{TARGET}']")
                next_elem = elem.find_element(By.XPATH, "following-sibling::td[1]")

                if "please" not in next_elem.text.lower():
                    self.bot.send_message(self.chat_id, f"{TARGET} {next_elem.text}")

                driver.quit()
            except Exception as e:
                traceback.print_exc()

            print(datetime.datetime.now(), "Sleeping...")

            time.sleep(60 * 5 + random.randint(5, 10))  # 5 min

    def start(self):
        Thread(target=self._loop).start()  # endless thread
