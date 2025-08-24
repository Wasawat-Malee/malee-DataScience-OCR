import json, pathlib, cv2, numpy as np
from skimage.metrics import structural_similarity as ssim

BASE = pathlib.Path(__file__).resolve().parents[1]
IMG_A = BASE / "data" / "images" / "img_a.png"
IMG_B = BASE / "data" / "images" / "img_b.png"
VID   = BASE / "data" / "video"  / "sample.mp4"
DIST  = BASE / "dist"
DIST.mkdir(exist_ok=True, parents=True)

def image_diff(a_path, b_path, thresh=0.25):
    a = cv2.imread(str(a_path))
    b = cv2.imread(str(b_path))
    g1 = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    score, diff = ssim(g1, g2, full=True)
    diff = (1 - diff)  # ส่วนที่ต่าง
    # สร้าง mask พื้นที่ที่ต่างอย่างมีนัยยะ
    mask = (diff > thresh).astype("uint8") * 255
    mask = cv2.dilate(mask, np.ones((5,5),np.uint8), iterations=2)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        if w*h < 50:  # กำจัด noise เล็ก ๆ
            continue
        boxes.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h)})
    return {"ssim": float(round(score,4)), "diff_boxes": boxes}

def analyze_video(video_path, step=3):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return {"error": "cannot open video"}
    fps = cap.get(cv2.CAP_PROP_FPS) or 10
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    back = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=50, detectShadows=False)

    events = []
    frame_idx = 0
    persons_total = 0
    movement_total = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        if frame_idx % step == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # คน (HOG) — อาจพลาดในวิดีโอตัวอย่างเรียบ ๆ แต่เราบันทึกผลไว้
            rects, _ = hog.detectMultiScale(gray, winStride=(8,8))
            persons = len(rects)
            persons_total += persons

            # การเคลื่อนไหว (fallback)
            fg = back.apply(gray)
            mov_area = int((fg > 0).sum())
            movement = mov_area > 500  # ธรณีอย่างง่าย
            movement_total += int(movement)

            t = round(frame_idx / fps, 2)
            if persons or movement:
                events.append({"t": t, "persons": persons, "movement": bool(movement)})
        frame_idx += 1

    cap.release()
    return {
        "fps": float(fps),
        "events": events,
        "person_detected_any": persons_total > 0,
        "movement_detected_any": movement_total > 0
    }

def run():
    out = {
        "image_diff": image_diff(IMG_A, IMG_B),
        "video_detection": analyze_video(VID)
    }
    (DIST/"vision_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[ok] dist/vision_results.json")

if __name__ == "__main__":
    run()

