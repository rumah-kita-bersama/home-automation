import os
import yaml

import ragil

# import doorbell
# import machine
# import imei


def main():
    secrets = load_secrets("secrets.yaml")

    ragil.start(secrets.get("ragil"))

    # disable doorbel, not used
    # doorbell.start(secrets.get("doorbell"))

    # disable machine, not used
    # machine.start(secrets.get("machine"))

    # disable imei
    # imei.start(secrets.get("imei"))


def load_secrets(filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path) as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    print("Starting...")
    main()
