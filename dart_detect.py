# 的のまわり(注目する範囲 = ROI)だけを見て、ダーツが刺さったかを判定する
#   起動したら: 映像の上で的のまわりをマウスでドラッグして四角を作り、Enter
#   次に: target ウィンドウで、真ん中の丸のふちを 5〜8 か所クリック(黄色い輪ができる)
#   m キー: 真ん中の丸をやり直す
#   b キー: 今の画像を「刺さる前(基準)」として保存する
#   u / j キー: 「変化あり」とみなす差を 大きく / 小さく する
#   c キー: 細い線・小さい点を消す処理の オン / オフ
#   r キー: 範囲を選び直す
#   q キー: 終了

import cv2
import numpy as np
from camera_setup import open_camera

diff_level = 5     # 色がこれ以上変わった点を「変化あり」とみなす(0〜255)。5 でバレルと影まで映る
DART_AREA = 400    # いちばん大きいかたまりがこれ以上なら「ダーツが刺さった」とみなす(画面の biggest を見て調整)
SHOW_WIDTH = 600   # 範囲を拡大して表示するときの横幅
CLEAN_SIZE = 3     # これより細い線・小さい点を消す(大きくするほど強く消える。バレルまで消えたら小さくする)
clean_on = True    # c キーで オン / オフ を切り替えて、効果を見比べられる


def smooth(frame):
    # 少しぼかす(細かいザラザラを減らすため)
    return cv2.GaussianBlur(frame, (5, 5), 0)


def select_area(cap):
    # 映像を1枚取って、その上でマウスで範囲を選んでもらう
    for _ in range(10):  # カメラが落ち着くまで数枚読み捨てる
        cap.read()
    ok, frame = cap.read()
    print("的のまわりをマウスでドラッグして囲み、Enter を押してください")
    x, y, w, h = cv2.selectROI("select area", frame)
    cv2.destroyWindow("select area")
    return x, y, w, h


def find_tip(changed):
    # 白いかたまりの中から、ダーツの先端らしい点を探す
    # 1. 近くにある白い点どうしをつなげる(フライトとバレルが切れていても1つにするため)
    joined = cv2.morphologyEx(changed, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    # 2. 白いかたまりの「輪郭(ふちの線)」を取り出し、いちばん大きいものを選ぶ
    contours, _ = cv2.findContours(joined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return None, None, 0
    dart = max(contours, key=cv2.contourArea)
    # 3. かたまりの重心(全体の真ん中)を求める
    m = cv2.moments(dart)
    if m["m00"] == 0:
        return None, None, 0
    center = (m["m10"] / m["m00"], m["m01"] / m["m00"])
    # 4. 輪郭の点のうち、重心からいちばん遠い点 = 先端
    points = dart.reshape(-1, 2)
    distances = np.hypot(points[:, 0] - center[0], points[:, 1] - center[1])
    tip = points[distances.argmax()]
    area = int(cv2.contourArea(dart))  # いちばん大きいかたまりの面積(点の数くらい)
    return (int(tip[0]), int(tip[1])), (int(center[0]), int(center[1])), area


circle_points = []   # 真ん中の丸のふちをクリックした点(拡大表示の座標)
circle_shape = None  # クリックした点から作った「真ん中の丸」の形(たくさんの点でできた輪)


def on_click(event, mx, my, flags, param):
    # target ウィンドウがクリックされたときに OpenCV が呼んでくれる関数
    global circle_shape
    if event == cv2.EVENT_LBUTTONDOWN:
        circle_points.append((mx, my))
        if len(circle_points) >= 5:
            # 5点以上あれば、それらにいちばん合う「だ円」を OpenCV に計算してもらう
            # (斜めから見ると、まん丸は少しつぶれた だ円 に見えるため)
            (cx, cy), (width, height), angle = cv2.fitEllipse(np.array(circle_points, np.float32))
            # だ円を、ふちに並んだ点の集まり(多角形)に変換しておく
            circle_shape = cv2.ellipse2Poly((int(cx), int(cy)), (int(width / 2), int(height / 2)),
                                            int(angle), 0, 360, 5)


def open_target_window():
    cv2.namedWindow("target")
    cv2.setMouseCallback("target", on_click)  # クリックされたら on_click を呼ぶように登録


def enlarge(image):
    # 小さい範囲を見やすく拡大する
    h, w = image.shape[:2]
    return cv2.resize(image, (SHOW_WIDTH, int(h * SHOW_WIDTH / w)),
                      interpolation=cv2.INTER_NEAREST)


cap = open_camera()
x, y, w, h = select_area(cap)
if w == 0 or h == 0:
    print("範囲が選ばれなかったので終了します")
    cap.release()
    raise SystemExit

open_target_window()
base = None
print("target ウィンドウで、真ん中の丸のふちを 5〜8 か所クリックしてください(m でやり直し)")
print("ダーツが刺さっていない状態で b キーを押してください。q で終了")

while True:
    ok, frame = cap.read()
    if not ok:
        print("映像を読み込めませんでした")
        break

    area = smooth(frame[y:y + h, x:x + w])  # 選んだ範囲だけを切り出す
    view = enlarge(area)

    # クリックした点と、そこから作った真ん中の丸を黄色で描く
    for p in circle_points:
        cv2.circle(view, p, 3, (0, 255, 255), -1)
    if circle_shape is not None:
        cv2.polylines(view, [circle_shape], True, (0, 255, 255), 2)

    if base is not None:
        diff = cv2.absdiff(base, area).max(axis=2)
        _, changed = cv2.threshold(diff, diff_level, 255, cv2.THRESH_BINARY)
        if clean_on:
            # 細い線や小さな点を消す(マットが少しずれたり、ダーツが揺れたりしてできる差)
            # 「オープニング」= いったん白を細らせて細いものを消し、そのあと太らせて元の太さに戻す
            changed = cv2.morphologyEx(changed, cv2.MORPH_OPEN,
                                       np.ones((CLEAN_SIZE, CLEAN_SIZE), np.uint8))
        count = cv2.countNonZero(changed)
        tip, center, biggest = find_tip(changed)

        # 合計ではなく「いちばん大きいかたまり」の大きさで、ダーツかどうかを決める
        # (ほかのダーツが揺れた跡や小さな点は、ばらばらの小さいかたまりになるため)
        if biggest >= DART_AREA:
            cv2.putText(view, "DART!", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 4)
            if tip is not None:
                scale = SHOW_WIDTH / w  # 拡大表示に合わせて座標も拡大する
                tip_view = (int(tip[0] * scale), int(tip[1] * scale))
                center_view = (int(center[0] * scale), int(center[1] * scale))
                cv2.circle(view, center_view, 5, (255, 0, 0), -1)   # 青い点 = 重心
                cv2.circle(view, tip_view, 12, (0, 255, 0), 2)      # 緑の丸 = 先端
                cv2.putText(view, f"tip: {tip}", (20, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                # 先端が真ん中の丸の中にあるか、OpenCV に調べてもらう
                # (中なら プラス、ちょうどふちなら 0、外なら マイナス が返ってくる)
                if circle_shape is not None:
                    result = cv2.pointPolygonTest(circle_shape, (float(tip_view[0]), float(tip_view[1])), False)
                    if result >= 0:
                        cv2.putText(view, "IN!", (20, 190), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 255, 0), 4)
                    else:
                        cv2.putText(view, "OUT", (20, 190), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 4)
        cv2.putText(view, f"changed: {count}  biggest: {biggest}  level: {diff_level}", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("diff", enlarge(changed))
    else:
        cv2.putText(view, "press b", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("target", view)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("b"):
        base = area
        print("基準の画像を保存しました")
    elif key == ord("m"):
        circle_points.clear()
        circle_shape = None
        print("真ん中の丸をやり直します。ふちを 5〜8 か所クリックしてください")
    elif key == ord("c"):
        clean_on = not clean_on
        print("細い線を消す処理:", "オン" if clean_on else "オフ")
    elif key == ord("u"):
        diff_level += 5
    elif key == ord("j"):
        diff_level = max(diff_level - 5, 5)
    elif key == ord("r"):
        cv2.destroyAllWindows()
        new_area = select_area(cap)
        if new_area[2] > 0 and new_area[3] > 0:  # ちゃんと選ばれたときだけ変える
            x, y, w, h = new_area
        base = None  # 範囲が変わったので基準も取り直す
        circle_points.clear()  # 真ん中の丸も選び直す
        circle_shape = None
        open_target_window()
        print("範囲を選び直しました。b キーで基準を保存してください")

cap.release()
cv2.destroyAllWindows()
