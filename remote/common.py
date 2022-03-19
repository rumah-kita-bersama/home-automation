import json
import os

from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
import yaml


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

    def start(self):
        self.updater.start_polling(drop_pending_updates=True)

    def add_handler(self, handler):
        handler.register(self.updater.dispatcher)


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

    def register(self, dispatcher):
        dispatcher.add_handler(MessageHandler(Filters.text, self.handle))

    def _get_text(self, update):
        if update.channel_post:
            return update.channel_post.text

        return update.message.text
