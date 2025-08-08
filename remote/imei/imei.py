import requests
import pytesseract
import cv2
import numpy as np
import time
import os

from threading import Thread
from PIL import Image, ImageFilter
from io import BytesIO

ENABLED = False
SHOW_INFO = True
DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class IMEIChecker:

    def __init__(self, target, token, chat_id):
        self.target = target
        self.token = token
        self.chat_id = chat_id

    def loop(self):
        if not ENABLED:
            return

        s = requests.Session()

        found = False
        with open(os.path.join(DIR_PATH, "dump.txt"), "a") as f:
            while True:
                retries = 0
                while True:
                    if retries > 10:
                        break

                    if SHOW_INFO:
                        print("Retries:", retries, file=f)
                    try:
                        r = s.get(
                            "https://www.beacukai.go.id//images/captcha/captcha.png")
                        r.raise_for_status()

                        captcha = self.getCaptcha(r.content).strip()
                        if SHOW_INFO:
                            print("Captcha:", captcha, file=f)

                        if len(captcha) == 6:
                            payload = {
                                "content": "sendCekImei",
                                "txtCaptcha": str(captcha),
                                "txtImei": str(self.target)
                            }
                            r = s.post(
                                "https://www.beacukai.go.id/cek-imei.html", data=payload)
                            r.raise_for_status()

                            if SHOW_INFO:
                                print("Result:", r.status_code,
                                      r.content, file=f)

                            if r.content != b"null" and r.content != b"wrongcaptcha" and len(r.content) < 100:
                                found = True

                            if r.content != b"wrongcaptcha" and len(r.content) < 100:
                                break

                    except:
                        pass

                    f.flush()
                    retries += 1
                    time.sleep(2)

                if found:
                    break

                print("Waiting for 6 hours...", file=f)

                f.flush()
                time.sleep(6 * 60 * 60)  # 6 hours

            if found:
                print("Found, exiting...", file=f)

                text = "IMEI Ditemukan {}".format(self.target)
                url = "https://api.telegram.org/bot{}/sendMessage?text={}&chat_id={}"
                res = requests.get(url.format(self.token, text, self.chat_id))
                res.raise_for_status()

    def start(self):
        # invoke endless thread
        Thread(target=self.loop).start()

    def getCaptcha(self, img_content):
        img = Image.open(BytesIO(img_content))
        img_name = os.path.join(DIR_PATH, "image.png")
        img.save(img_name)

        w, h = img.size
        img = img.resize((2 * w, 2 * h))
        img = img.convert("L")
        img = img.point(lambda p: 0 if p > 130 else 255)
        img = img.filter(ImageFilter.SHARPEN)

        bw_img_name = os.path.join(DIR_PATH, "image-bw.png")
        img.save(bw_img_name)
        img = cv2.imread(bw_img_name, 0)

        h, w = img.shape
        img = cv2.resize(img, (w*5, h*5))

        # Threshold the image and find the contours
        _, thresh = cv2.threshold(img, 130, 255, cv2.THRESH_BINARY_INV)
        ctr, hie = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        inner_contours = []
        for contour, h in zip(ctr, hie[0]):

            # Ignore inside parts (circle in a 'p' or 'b')
            if h[3] == -1:
                inner_contours.append(contour)

        def sort_contours(contours):
            # construct the list of bounding boxes and sort them from top to bottom
            boundingBoxes = [cv2.boundingRect(c) for c in contours]
            (contours, boundingBoxes) = zip(
                *sorted(zip(contours, boundingBoxes), key=lambda b: b[1][0], reverse=False))

            # return the list of sorted contours
            return contours

        sorted_contours = sort_contours(inner_contours)
        # Create a white background iamge to paste the letters on
        bg = np.zeros((300, 1000), np.uint8)
        bg[:] = 255
        left = 5

        # Iterate through the contours
        for contour in sorted_contours:
            # Ignore inside parts (circle in a 'p' or 'b')

            # Get the bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            # Paste it onto the background
            bg[290-h:290, left:left+w] = img[y:y+h, x:x+w]
            left += (w + 15)

        fin_img_name = os.path.join(DIR_PATH, "final-img.png")
        final_img = Image.fromarray(bg)
        final_img.save(fin_img_name)
        return pytesseract.image_to_string(
            final_img,
            config="--psm 7 -l eng -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz0123456789",
        )


def start(secrets):
    token, chat_id = secrets["telegram"]["token"], secrets["telegram"]["chat_id"]
    target = secrets["target"]

    IMEIChecker(target, token, chat_id).start()
