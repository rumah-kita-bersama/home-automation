from common import AuthMiddleware, BaseHandler, TelegramBot, TuyaBulb, AirConditioner

RAGIL_K = "ragil"


class RagilHandler(BaseHandler):
    def __init__(self, bulb, ac):
        self.bulb = bulb
        self.ac = ac

    def handle(self, update, context):
        text = self._get_text(update)
        if text.startswith("lg"):
            try:
                val_t = text.removeprefix("lg").strip()
                if val_t == "x":
                    val = 0
                elif val_t == "m":
                    val = 500
                elif val_t == "h":
                    val = 750
                elif val_t == "l":
                    val = 250
                else:
                    val = int(val_t)

                if val == 0:
                    self.bulb.turn_off()
                else:
                    self.bulb.set_brightness(val)

            except Exception as e:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="err or invalid value (l, m, h, 10-999)" + str(e),
                )

        elif text.startswith("ac"):
            try:
                val_t, ok = text.removeprefix("ac").strip().split(), True
                kwargs = {
                    "temp": 25,
                    "off": False,
                    "swing": True,
                    "fan": True,
                }
                for val_x in val_t:
                    if not ok:
                        break

                    if val_x == "x":
                        kwargs["off"] = True
                    elif val_x == "sx":
                        kwargs["swing"] = False
                    elif val_x == "fx":
                        kwargs["fan"] = False
                    else:
                        kwargs["temp"] = int(val_x)

                ok = self.ac.set_cmd(**kwargs)
                if not ok:
                    raise Exception()

            except Exception:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text="err or invalid value"
                )

        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text="invalid command"
            )


def start(secrets):
    g = secrets.get("bulb")
    t = secrets.get("telegram")
    a = secrets.get("ac")

    ac = AirConditioner(a["ip"])
    bulb = TuyaBulb(g["ver"], g["id"], g["node_id"], g["key"], g["gw_id"])
    handler = RagilHandler(bulb, ac)

    auth_middleware = AuthMiddleware(*t["allowed_ids"])
    auth_middleware.apply(handler)

    bot = TelegramBot(t["token"])
    bot.add_handler(handler)
    bot.start()
