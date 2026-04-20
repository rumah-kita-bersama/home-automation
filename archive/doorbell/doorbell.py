import pigpio
import requests
import time


# TODO: need to be updated
class DoorBell:
    def __init__(self, pi, pin):
        self._last_event_ts = 0
        self._subscribers = []
        self._event_ts_threshold_micros = 6000000

        self.pi = pi
        self.pin = pin

    def add_subscriber(self, sub_fn):
        self._subscribers.append(sub_fn)

    def _notify_subscribers(self):
        for sub in self._subscribers:
            sub()

    def listen(self):
        self.pi.callback(self.pin, pigpio.EITHER_EDGE, self._callback)

    def _callback(self, pin, value, tick):
        ts = time.time_ns() // 1000
        if ts - self._last_event_ts >= self._event_ts_threshold_micros:
            self._last_event_ts = ts
            self._notify_subscribers()


class DoorBellTelegramNotifier:
    def __init__(self, bot_token, chat_id, door_bell):
        self._bot_token = bot_token
        self._chat_id = chat_id

        door_bell.add_subscriber(self._handle_button_pressed)

    def _handle_button_pressed(self):
        self._send_to_telegram("Assalamualaikum, ada orang di depan.")

    def _send_to_telegram(self, text):
        url = "https://api.telegram.org/bot{}/sendMessage?text={}&chat_id={}"
        res = requests.get(url.format(self._bot_token, text, self._chat_id))
        res.raise_for_status()


def start(secret):
    pi = pigpio.pi()
    gpio_pin = 4

    doorbell = DoorBell(pi, gpio_pin)
    doorbell.listen()

    bot_token, channel_id = (
        secret["telegram"]["token"],
        secret["telegram"]["channel_id"],
    )
    notifier = DoorBellTelegramNotifier(bot_token, channel_id, doorbell)
