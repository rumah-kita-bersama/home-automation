import time
import threading

from common import AuthMiddleware, BaseHandler, TelegramBot, Tradfri, AirConditioner


class LightHandler(BaseHandler):
    def __init__(self, tradfri, light_id):
        self.tradfri = tradfri
        self.light_id = light_id

    def handle(self, update, context):
        text = self._get_text(update)
        if not text.startswith("light"):
            return

        try:
            val = int(text.removeprefix("light "))
        except ValueError:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="invalid value (valid range: 0-254)")
            return

        self.tradfri.set_light_dimmer_value(int(self.light_id), val)


class ACHandler(BaseHandler):
    def __init__(self, ac):
        self._ac = ac
        self._timer = None

    def handle(self, update, context):
        text = self._get_text(update)
        if not text.startswith("ac"):
            return

        params = text.removeprefix("ac ")
        if params == "off":
            self._turn_off()
            return

        try:
            temp = int(params)
            self._set_temp(temp)
            return
        except ValueError:
            pass

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="invalid command",
        )

    def _turn_off(self):
        # send twice because somehow my ac put on timer if only send once.
        self._ac.set_cmd(temp=26, off=True)
        time.sleep(0.5)
        self._ac.set_cmd(temp=26, off=True)

    def _set_temp(self, temp):
        self._ac.set_cmd(temp=temp, fan=1)
            
        # auto turn off after some time
        turn_off_after_secs = 60 * 60 # 1hr

        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(turn_off_after_secs, self._turn_off)
        self._timer.start()


def start(secrets):
    g = secrets.get("gateway")
    t = secrets.get("telegram")

    tradfri = Tradfri(g["ip"], g["identity"], g["psk"])
    light_handler = LightHandler(tradfri, g["light_id"])

    ac = AirConditioner(secrets["ac"]["ip"])
    ac_handler = ACHandler(ac)

    auth_middleware = AuthMiddleware(*t["allowed_ids"])
    auth_middleware.apply(light_handler)
    auth_middleware.apply(ac_handler)

    bot = TelegramBot(t["token"])
    bot.add_handler(light_handler)
    bot.add_handler(ac_handler)
    bot.start()
