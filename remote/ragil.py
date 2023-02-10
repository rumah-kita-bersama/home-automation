from common import (
    AuthMiddleware,
    BaseHandler,
    TelegramBot,
    Tradfri,
    AirConditioner
)

RAGIL_K = "ragil"


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
                if val_t == "x":
                    val = 0
                elif val_t == "m":
                    val = 128
                elif val_t == "h":
                    val = 192
                elif val_t == "l":
                    val = 64
                else:
                    val = int(val_t)

                self.tradfri.set_light_dimmer_value(int(self.light_id), val)

            except Exception as e:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text="err or invalid value (l, m, h, 0-254)" + str(e))

        elif text.startswith("ac"):
            try:
                val_t, ok = text.removeprefix("ac").strip(), False
                if val_t == "z":
                    ok = self.ac.set_cmd(temp=26)
                elif val_t == "x":
                    ok = self.ac.set_cmd(off=True)
                elif val_t == "sz":
                    ok = self.ac.set_cmd(swing=True)
                elif val_t == "sx":
                    ok = self.ac.set_cmd(swing=False)
                else:
                    ok = self.ac.set_cmd(temp=int(val_t))

                if not ok:
                    raise Exception()

            except Exception:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text="err or invalid value")

        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="invalid command")


def start(secrets):
    g = secrets.get("gateway")
    t = secrets.get("telegram")
    a = secrets.get("ac")

    ac = AirConditioner(a["ip"])
    tradfri = Tradfri(g["ip"], g["identity"], g["psk"])
    handler = RagilHandler(tradfri, g["light_id"], ac)

    auth_middleware = AuthMiddleware(*t["allowed_ids"])
    auth_middleware.apply(handler)

    bot = TelegramBot(t["token"])
    bot.add_handler(handler)
    bot.start()
