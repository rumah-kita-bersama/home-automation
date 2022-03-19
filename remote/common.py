import const

import requests
from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from telegram.ext import Filters, MessageHandler, Updater


class AirConditioner:
    def __init__(self, ip):
        self.ip = ip

    def set_cmd(self, temp=27, off=False, fix=False, mode=const.AC_MODE_AUTO, fan=const.AC_FAN_AUTO, swing=const.AC_SWING_NO_OP):
        url = "http://{}/".format(self.ip)
        r = requests.get(url, params={
            "off": 1 if off else 0,
            "fix": 1 if fix else 0,
            "mode": mode,
            "temp": temp,
            "fan": fan,
            "swing": swing,
        })
        return r.status_code == 200


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
        self.updater = Updater(token=token, use_context=True)
        self._text_handlers = []

    def start(self):
        self.updater.dispatcher.add_handler(
            MessageHandler(Filters.text, self._handle_text))
        self.updater.start_polling(drop_pending_updates=True)

    def add_handler(self, handler):
        self._text_handlers.append(handler)

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
