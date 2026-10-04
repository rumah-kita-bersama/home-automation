import os
import yaml

from ac.ac import AC
from common import AuthMiddleware, TelegramBot, TuyaBulb
from bulbac import BulbACHandler


def main():
    secrets = load_secrets("secrets.yaml")

    b = secrets.get("bulb")
    bulb = TuyaBulb(b["ver"], b["id"], b["node_id"], b["key"], b["gw_id"], b.get("ip"))

    ac = AC()

    handler = BulbACHandler(bulb, ac)

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
    main()
