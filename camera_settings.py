# カメラの設定(露出・ホワイトバランスなど)を確認するためのプログラム
#   s キー: カメラの設定画面を開く(Windows のみ)
#   p キー: 今の設定の数値を表示する
#   q キー: 終了

import sys
import cv2

CAMERA_NUMBER = 0

if sys.platform == "win32":
    cap = cv2.VideoCapture(CAMERA_NUMBER, cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(CAMERA_NUMBER)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("カメラを開けませんでした")
    sys.exit()


def print_settings():
    # カメラが「今こうなっています」と答えた数値を表示する
    print("---- 今の設定 ----")
    print("自動露出      :", cap.get(cv2.CAP_PROP_AUTO_EXPOSURE))
    print("露出          :", cap.get(cv2.CAP_PROP_EXPOSURE))
    print("明るさ        :", cap.get(cv2.CAP_PROP_BRIGHTNESS))
    print("ゲイン        :", cap.get(cv2.CAP_PROP_GAIN))
    print("自動WB        :", cap.get(cv2.CAP_PROP_AUTO_WB))
    print("色温度(WB)    :", cap.get(cv2.CAP_PROP_WB_TEMPERATURE))


print("s: 設定画面を開く / p: 設定の数値を表示 / q: 終了")
print_settings()

while True:
    ok, frame = cap.read()
    if not ok:
        print("映像を読み込めませんでした")
        break

    cv2.imshow("camera", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("s"):
        cap.set(cv2.CAP_PROP_SETTINGS, 1)  # カメラドライバの設定画面を開く
    elif key == ord("p"):
        print_settings()

cap.release()
cv2.destroyAllWindows()
