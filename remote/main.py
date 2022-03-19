import os
import yaml

import fata
import ragil
import doorbell


def main():
    secrets = load_secrets("secrets.yaml")

    fata.start(secrets.get("fata"))
    ragil.start(secrets.get("ragil"))
    doorbell.start(secrets.get("doorbell"))


def load_secrets(filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path) as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    print("Starting...")
    main()
