import os
import yaml

from acv2.acv2 import ACV2
from cdc.cdc import CDC2BChecker
from common import AuthMiddleware, TelegramBot, TuyaBulb, AirConditioner
from bulbac import BulbACHandler


def main():
    secrets = load_secrets("secrets.yaml")

    t = secrets.get("telegram")
    bot = TelegramBot(t["token"])

    b = secrets.get("bulb")
    bulb = TuyaBulb(b["ver"], b["id"], b["node_id"], b["key"], b["gw_id"])

    # a = secrets.get("ac")
    # ac = AirConditioner(a["ip"]) # old AC

    ac = ACV2() # new AC
    bulb_ac_handler = BulbACHandler(bulb, ac)

    auth = AuthMiddleware(*t["allowed_ids"])
    auth.apply(bulb_ac_handler)

    bot.add_handler(bulb_ac_handler)
    bot.start()

    c = secrets.get("cdc")
    cdc = CDC2BChecker(bot, c["telegram_channel_id"])
    cdc.start()


def load_secrets(filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path) as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    print("Starting...")
    main()
