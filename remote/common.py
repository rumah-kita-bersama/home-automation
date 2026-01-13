import requests
import tinytuya
import tinytuya.core
from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from telegram.ext import Filters, MessageHandler, Updater


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
        try:
            self.gateway = tinytuya.BulbDevice(
                version=version, dev_id=gw_id, address="Auto", local_key=key
            )
            self.bulb = tinytuya.BulbDevice(
                version=version,
                dev_id=dev_id,
                address="Auto",
                local_key=key,
                node_id=node_id,
                parent=self.gateway,
            )
        except:
            self.bulb = None

    def turn_off(self):
        if self.bulb is None:
            return None

        self.bulb.turn_off()

    def set_brightness(self, brightness):
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

        self.bulb.turn_on(nowait=False)
        return self.bulb._send_receive(payload, getresponse=False)


class Tradfri:
    def __init__(self, host, identity, psk):
        api_factory = APIFactory(host=host, psk_id=identity, psk=psk)
        self.request = api_factory.request
        self.gateway = Gateway()

        self._light_cache = {}

    def set_light_dimmer_value(self, light_id, value):
        light = self._get_light(light_id)
        cmd = light.light_control.set_dimmer(value)
        self.request(cmd)

    def _get_light(self, id):
        light = self._light_cache.get(id)
        if light:
            return light

        devices_command = self.gateway.get_devices()
        devices_commands = self.request(devices_command)
        devices = self.request(devices_commands)
        for device in devices:
            if device.has_light_control:
                self._light_cache[device.id] = device

        return self._light_cache.get(id)


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
