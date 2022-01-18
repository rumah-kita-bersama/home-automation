from common import (
    AuthMiddleware,
    BaseHandler,
    TelegramBot,
    Tradfri,
    load_secrets,    
)

import requests

RAGIL_K = "ragil"

class AC:
    def __init__(self, ip):
        self.ip = ip

    def set_temp(self, temp):
        url = "http://{}/".format(self.ip)
        r = requests.get(url, params={"cmd": temp})
        return r.status_code == 200


class RagilHandler(BaseHandler):

    def __init__(self, tradfri, light_id, ac):
        self.tradfri = tradfri
        self.light_id = light_id
        self.ac = ac

    def handle(self, update, context):
        text = self._get_text(update)
        if text.startswith("lg"):
            try:
                val_t = text.removeprefix("lg").strip()
                if val_t == "m":
                    val = 128
                elif val_t == "h":
                    val = 192
                elif val_t == "l":
                    val = 64                
                else:
                    val = int(val_t)
                
                self.tradfri.set_light_dimmer_value(int(self.light_id), val)

            except Exception as e:
                context.bot.send_message(chat_id=update.effective_chat.id, text="err or invalid value (l, m, h, 0-254)")
    
        elif text.startswith("ac"):
            try:
                val_t = text.removeprefix("ac").strip()
                if val_t == "z":
                    val = 16
                elif val_t == "x":
                    val = 0
                else:
                    val = int(val_t)

                ok = self.ac.set_temp(val)
                if not ok:
                    raise Exception()

            except Exception:
                context.bot.send_message(chat_id=update.effective_chat.id, text="err or invalid value (z, x, 0, 16-32)")            

        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="invalid command")


def startRagil():
    secrets = load_secrets(RAGIL_K)
    g = secrets.get("gateway")
    t = secrets.get("telegram")
    a = secrets.get("ac")

    ac = AC(a["ip"])
    tradfri = Tradfri(g["ip"], g["identity"], g["psk"])    
    handler = RagilHandler(tradfri, g["light_id"], ac)

    auth_middleware = AuthMiddleware(*t["allowed_ids"])
    auth_middleware.apply(handler)

    bot = TelegramBot(t["token"])
    bot.add_handler(handler)
    bot.start()
