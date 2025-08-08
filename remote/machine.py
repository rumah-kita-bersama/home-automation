import time
from threading import Thread

import requests
import tuyapower


class WashingMachine:
    SCAN_PERIOD = 30 * 60
    SUM_PERIOD = 12 * 60
    TEXT_START = "Nyuci trooos"
    TEXT_FINISH = "Mesin cuci sudah selesai. Jangan lupa dijemur!"

    class TuyaPowerDevice:
        def __init__(self, id, ip, key, ver):
            self.id = id
            self.ip = ip
            self.key = key
            self.ver = ver

        def get_electric_current(self):
            info = tuyapower.deviceInfo(self.id, self.ip, self.key, self.ver)
            return info[1]

    def __init__(self, device_id, device_key, device_ver, bot_token, chat_id):
        self._o = None
        self._lsc = -self.SCAN_PERIOD

        self._device_id = device_id
        self._device_key = device_key
        self._device_ver = device_ver
        self._bot_token = bot_token
        self._chat_id = chat_id

    def _send_to_telegram(self, text):
        url = "https://api.telegram.org/bot{}/sendMessage?text={}&chat_id={}"
        res = requests.get(url.format(self._bot_token, text, self._chat_id))
        res.raise_for_status()

    def _should_rescan(self, ts):
        return (self._o is None) or (ts - self._lsc >= self.SCAN_PERIOD)

    def _rescan(self, ts):
        devices = tuyapower.deviceScan()
        for ip_addr, info in devices.items():
            if info.get("gwId", "") == self._device_id:
                self._o = self.TuyaPowerDevice(
                    self._device_id,
                    ip_addr,
                    self._device_key,
                    self._device_ver,
                )
        self._lsc = ts

    def start(self):
        def loop():
            nums, running, ts = [], False, 0
            while True:
                total = sum(nums)
                if total == 0 and running:
                    running = False
                    self._send_to_telegram(self.TEXT_FINISH)
                elif total == 0 and self._should_rescan(ts):
                    self._rescan(ts)
                elif total > 0:
                    if not running:
                        self._send_to_telegram(self.TEXT_START)
                    running = True

                curr = 0
                if self._o:
                    curr = self._o.get_electric_current()
                    if len(nums) >= self.SUM_PERIOD:
                        nums = nums[1:]
                    nums.append(int(curr))

                ts = ts + 1
                time.sleep(1)

        # invoke endless thread
        Thread(target=loop).start()


def start(secrets):
    bot_token, channel_id = (
        secrets["telegram"]["token"],
        secrets["telegram"]["channel_id"],
    )
    device_id, device_key, device_ver = (
        secrets["device"]["id"],
        secrets["device"]["key"],
        secrets["device"]["ver"],
    )

    WashingMachine(device_id, device_key, device_ver, bot_token, channel_id).start()
