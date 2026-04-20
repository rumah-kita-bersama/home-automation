import os
import yaml

from acv3.acv3 import ACV3 
from common import AuthMiddleware, TelegramBot, TuyaBulb, TuyaAirPurifier
from bulbac import BulbACHandler


def main():
    secrets = load_secrets("secrets.yaml")

    b = secrets.get("bulb")
    bulb = TuyaBulb(b["ver"], b["id"], b["node_id"], b["key"], b["gw_id"])

    p = secrets.get("purifier")
    purifier = TuyaAirPurifier(p["ver"], p["id"], p["key"])

    ac = ACV3()

    handler = BulbACHandler(bulb, ac, purifier)

    t = secrets.get("telegram")
    bot = TelegramBot(t["token"])

    auth = AuthMiddleware(*t["allowed_ids"])
    auth.apply(handler)

    bot.add_handler(handler)
    bot.start()

def load_secrets(filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path) as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    print("Starting...")
    main()
