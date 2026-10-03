import logging

import requests
import tinytuya
import tinytuya.core
from telegram.ext import Filters, MessageHandler, Updater

log = logging.getLogger(__name__)


class AirConditioner:
    def __init__(self, ip):
        self.ip = ip

    def set_cmd(self, temp=26, off=False, swing=True, fan=True):
        url = "http://{}/".format(self.ip)
        r = requests.get(
            url,
            params={
                "off": 1 if off else 0,
                "swing": 1 if swing else 0,
                "fan": 1 if fan else 0,
                "temp": temp,
            },
        )
        return r.status_code == 200


class TuyaBulb:
    def __init__(self, version, dev_id, node_id, key, gw_id):
        self.version = version
        self.dev_id = dev_id
        self.node_id = node_id
        self.key = key
        self.gw_id = gw_id
        self.gateway = None
        self.bulb = None
        self._connect()

    def _connect(self):
        try:
            gateway = tinytuya.BulbDevice(
                version=self.version, dev_id=self.gw_id, address="Auto", local_key=self.key
            )
            bulb = tinytuya.BulbDevice(
                version=self.version,
                dev_id=self.dev_id,
                address="Auto",
                local_key=self.key,
                node_id=self.node_id,
                parent=gateway,
            )
        except Exception:
            return

        self._disconnect()  # close the old connection

        self.gateway = gateway
        self.bulb = bulb

    def _disconnect(self):
        self._close(self.bulb)
        self._close(self.gateway)
        self.bulb = None
        self.gateway = None

    def _close(self, device):
        if device is not None and device.socket:
            device.socket.close()
            device.socket = None

    def turn_off(self):
        if self.bulb is None:
            self._connect()
        if self.bulb is None:
            return None

        try:
            self.bulb.turn_off()
        except Exception:
            log.exception("failed to send command to bulb")
            self._disconnect()

    def set_brightness(self, brightness):
        if self.bulb is None:
            self._connect()
        if self.bulb is None or brightness < 10 or brightness > 999:
            return None

        payload = self.bulb.generate_payload(
            tinytuya.core.CONTROL,
            {
                self.bulb.DPS_INDEX_MODE[self.bulb.bulb_type]: self.bulb.DPS_MODE_WHITE,
                self.bulb.DPS_INDEX_BRIGHTNESS[self.bulb.bulb_type]: brightness,
                self.bulb.DPS_INDEX_COLOURTEMP[self.bulb.bulb_type]: 0,
            },
        )

        try:
            self.bulb.turn_on(nowait=False)
            return self.bulb._send_receive(payload, getresponse=False)
        except Exception:
            log.exception("failed to send command to bulb")
            self._disconnect()
            return None


class TuyaAirPurifier:
    def __init__(self, version, dev_id, key):
        self.version = version
        self.dev_id = dev_id
        self.key = key
        self.purifier = None
        self._connect()

    def _connect(self):
        try:
            purifier = tinytuya.OutletDevice(
                version=self.version,
                dev_id=self.dev_id,
                address="Auto",
                local_key=self.key,
            )
        except Exception:
            return

        self._disconnect()  # close the old connection

        self.purifier = purifier

    def _disconnect(self):
        if self.purifier is not None and self.purifier.socket:
            self.purifier.socket.close()
            self.purifier.socket = None
        self.purifier = None

    def _call(self, fn):
        if self.purifier is None:
            self._connect()
        if self.purifier is None:
            return None

        try:
            return fn()
        except Exception:
            log.exception("failed to send command to purifier")
            self._disconnect()
            return None

    def turn_on(self):
        return self._call(lambda: self.purifier.set_value(1, True))

    def turn_off(self):
        return self._call(lambda: self.purifier.set_value(1, False))

    def set_fan_speed(self, speed):
        """
        Controls the fan speed using DPS Index 4.
        Typical string values might be "low", "mid", "high", "auto".
        """
        return self._call(lambda: self.purifier.set_value(4, speed))

    def reset_filter(self):
        """
        Resets the filter using DPS Index 11.
        """
        return self._call(lambda: self.purifier.set_value(11, True))


class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.updater = Updater(token=token, use_context=True)

        self._text_handlers = []

    def start(self):
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.text, self._handle_text)
        )
        self.updater.start_polling(drop_pending_updates=True)

    def add_handler(self, handler):
        self._text_handlers.append(handler)

    def send_message(self, chat_id, text):
        url = "https://api.telegram.org/bot{}/sendMessage?text={}&chat_id={}"
        res = requests.get(url.format(self.token, text, chat_id))
        res.raise_for_status()

    def _handle_text(self, update, context):
        for handler in self._text_handlers:
            handler.handle(update, context)


def only_allow(allowed_ids):
    def decorate(fn):
        def get_chat_id(update):
            if update.channel_post:
                return update.channel_post.chat.id

            return update.message.chat.id

        def handle(update, context):
            if str(get_chat_id(update)) not in allowed_ids:
                return

            return fn(update, context)

        return handle

    return decorate


class AuthMiddleware:
    def __init__(self, *allowed_ids):
        self.allowed_ids = allowed_ids

    def apply(self, handler):
        handler.handle = only_allow(self.allowed_ids)(handler.handle)


class BaseHandler:
    def handle(self, update, context):
        raise NotImplementedError()

    def _get_text(self, update):
        if update.channel_post:
            return update.channel_post.text

        return update.message.text
