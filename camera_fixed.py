# 露出・ホワイトバランスなどを「手動・固定」にしてカメラ映像を表示する
#   w / s キー: 露出を明るく / 暗く
#   d キー    : カメラの設定画面を開く(Windows のみ)
#   p キー    : 今の設定の数値を表示する
#   q キー    : 終了

import sys
import cv2

CAMERA_NUMBER = 0

# ---- 固定したい値(あとでちょうどよい値に調整する) ----
EXPOSURE = -3         # 露出。数字が大きいほど明るい(-3 は約 1/8 秒)。-6 だと部屋が暗くて真っ暗だった
GAIN = 8             # ゲイン(映像を電気的に明るくする量)
BACKLIGHT = 0         # 逆光補正。0 = オフ
# --------------------------------------------------------

if sys.platform == "win32":
    cap = cv2.VideoCapture(CAMERA_NUMBER, cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(CAMERA_NUMBER)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("カメラを開けませんでした。他のプログラムがカメラを使っていないか確認してください。")
    sys.exit()

# 値を入れると、その項目は「自動」から「手動」に切り替わる
cap.set(cv2.CAP_PROP_EXPOSURE, EXPOSURE)
# ホワイトバランスは、プログラムから手動にすると青がほぼ消える(C270 + Windows で確認)ので、
# いまは設定画面(d キー)で試している
cap.set(cv2.CAP_PROP_GAIN, GAIN)
cap.set(cv2.CAP_PROP_BACKLIGHT, BACKLIGHT)


def print_settings():
    print("---- 今の設定 ----")
    print("露出          :", cap.get(cv2.CAP_PROP_EXPOSURE))
    print("自動WB        :", cap.get(cv2.CAP_PROP_AUTO_WB))
    print("ホワイトバランス:", cap.get(cv2.CAP_PROP_WB_TEMPERATURE))
    print("ゲイン        :", cap.get(cv2.CAP_PROP_GAIN))
    print("逆光補正      :", cap.get(cv2.CAP_PROP_BACKLIGHT))


print("w/s: 露出 明るく/暗く  d: 設定画面  p: 設定を表示  q: 終了")
print_settings()

exposure = EXPOSURE
while True:
    ok, frame = cap.read()
    if not ok:
        print("映像を読み込めませんでした")
        break

    # 画面の左上に今の露出を表示する
    cv2.putText(frame, f"exposure: {exposure}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    cv2.imshow("camera", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("w"):
        exposure = min(exposure + 1, 0)  # C270 は 0 が上限(それ以上は効かない)
        cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
    elif key == ord("s"):
        exposure -= 1
        cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
    elif key == ord("d"):
        cap.set(cv2.CAP_PROP_SETTINGS, 1)
    elif key == ord("p"):
        print_settings()

cap.release()
cv2.destroyAllWindows()
