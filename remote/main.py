import os
import yaml

from fata import start_fata
from ragil import start_ragil
from door_bell import start_door_bell


def main():
    secrets = load_secrets("secrets.yaml")

    start_fata(secrets.get("fata"))
    start_ragil(secrets.get("ragil"))
    start_door_bell(secrets.get("doorbell"))


def load_secrets(filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path) as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    print("Starting...")
    main()
