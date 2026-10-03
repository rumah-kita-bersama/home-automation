import logging

from ac import AC

def main():
    ac = AC()

    # Default settings: temp=26, off=False, swing=True, fan=True
    success = ac.set_cmd(temp=26, off=False, swing=True, fan=True)

    if not success:
        logging.error("failed to send command to AC (no exception raised, check IR hardware)")

if __name__ == '__main__':
    main()
