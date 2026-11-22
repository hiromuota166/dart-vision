# カメラを開いて、露出などを固定する「共通の部品」
# ほかのプログラムから  from camera_setup import open_camera  として使う

import sys
import cv2

CAMERA_NUMBER = 0
EXPOSURE = 0    # 露出。C270n は 0 が上限(いちばん明るい)
GAIN = 8        # ゲイン
BACKLIGHT = 0   # 逆光補正。0 = オフ


def open_camera():
    if sys.platform == "win32":
        cap = cv2.VideoCapture(CAMERA_NUMBER, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(CAMERA_NUMBER)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("カメラを開けませんでした。他のプログラムがカメラを使っていないか確認してください。")
        sys.exit()

    cap.set(cv2.CAP_PROP_EXPOSURE, EXPOSURE)
    cap.set(cv2.CAP_PROP_GAIN, GAIN)
    cap.set(cv2.CAP_PROP_BACKLIGHT, BACKLIGHT)
    return cap
