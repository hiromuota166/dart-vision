# 「刺さる前」と「今」の画像を比べて、変わった場所を白く表示する
#   b キー: 今の画像を「刺さる前(基準)」として保存する
#   u / j キー: 「変化あり」とみなす差を 大きく / 小さく する
#   q キー: 終了

import cv2
from camera_setup import open_camera

diff_level = 20  # 色がこれ以上変わった点を「変化あり」とみなす(0〜255)


def smooth(frame):
    # 少しぼかす(細かいザラザラを減らすため)
    return cv2.GaussianBlur(frame, (5, 5), 0)


cap = open_camera()
base = None  # 基準の画像(まだない)
print("ダーツが刺さっていない状態で b キーを押してください。q で終了")

while True:
    ok, frame = cap.read()
    if not ok:
        print("映像を読み込めませんでした")
        break

    now = smooth(frame)

    if base is not None:
        # 青・緑・赤それぞれの差を計算して、いちばん大きく変わった色の差を使う
        # (白黒だと「黄色」と「白」がほぼ同じ明るさになり、違いが分からないため)
        diff = cv2.absdiff(base, now).max(axis=2)
        _, changed = cv2.threshold(diff, diff_level, 255, cv2.THRESH_BINARY)
        count = cv2.countNonZero(changed)  # 白い点の数
        cv2.putText(frame, f"changed: {count}  level: {diff_level}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        cv2.imshow("diff", cv2.resize(changed, (640, 360)))  # 小さくして表示
    else:
        cv2.putText(frame, "press b", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

    cv2.imshow("camera", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("b"):
        base = now
        print("基準の画像を保存しました")
    elif key == ord("u"):
        diff_level += 5
    elif key == ord("j"):
        diff_level = max(diff_level - 5, 5)

cap.release()
cv2.destroyAllWindows()
