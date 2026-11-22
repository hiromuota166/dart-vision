# カメラ映像を画面に表示するだけのテスト
# 終了するには、映像のウィンドウを選んだ状態で q キーを押す

import sys
import cv2

CAMERA_NUMBER = 0  # PCにつないだカメラの番号(1台だけなら 0)

# Windows では DirectShow という方式でカメラを開く(起動が速く、あとで露出などを固定しやすい)
# Mac では自動で選ばせる
if sys.platform == "win32":
    cap = cv2.VideoCapture(CAMERA_NUMBER, cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(CAMERA_NUMBER)

# C270 の最大解像度 1280x720 をお願いする
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print("カメラを開けませんでした。USBの接続や、他のアプリがカメラを使っていないか確認してください。")
    sys.exit()

# 実際に使われている解像度を表示(お願いどおりになったか確認)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"解像度: {width} x {height}")
print("終了するには映像ウィンドウで q キーを押してください")

while True:
    ok, frame = cap.read()  # カメラから1枚(1フレーム)読み込む
    if not ok:
        print("映像を読み込めませんでした")
        break

    cv2.imshow("camera", frame)  # 画面に表示する

    # 1ミリ秒だけキー入力を待つ。q が押されたら終了
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()            # カメラを手放す
cv2.destroyAllWindows()  # ウィンドウを閉じる
