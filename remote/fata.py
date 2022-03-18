from common import (
    AuthMiddleware,
    BaseHandler,
    TelegramBot,
    Tradfri,
    load_secrets,
)

FATA_K = "fata"


class FataLightHandler(BaseHandler):

    def __init__(self, tradfri, light_id):
        self.tradfri = tradfri
        self.light_id = light_id

    def handle(self, update, context):
        text = self._get_text(update)
        if not text.startswith("light"):
            return

        try:
            val = int(text.removeprefix("light "))
        except Exception:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="invalid value (valid range: 0-254)")
            return

        self.tradfri.set_light_dimmer_value(int(self.light_id), val)


def start_fata():
    secrets = load_secrets(FATA_K)
    g = secrets.get("gateway")
    t = secrets.get("telegram")

    tradfri = Tradfri(g["ip"], g["identity"], g["psk"])
    light_handler = FataLightHandler(tradfri, g["light_id"])

    auth_middleware = AuthMiddleware(*t["allowed_ids"])
    auth_middleware.apply(light_handler)

    bot = TelegramBot(t["token"])
    bot.add_handler(light_handler)
    bot.start()
