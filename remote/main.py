import os
import yaml

import ragil

# import doorbell
# import machine
# import imei

import cdc


def main():
    secrets = load_secrets("secrets.yaml")

    ragil.start(secrets.get("ragil"))

    # doorbell.start(secrets.get("doorbell"))

    # machine.start(secrets.get("machine"))

    # imei.start(secrets.get("ragil"))

    cdc.start(secrets.get("ragil"))


def load_secrets(filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path) as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    print("Starting...")
    main()
