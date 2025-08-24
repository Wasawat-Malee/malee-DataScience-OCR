import os, cv2, numpy as np, pandas as pd, random, pathlib, fitz
from datetime import datetime, timedelta

BASE = pathlib.Path(__file__).resolve().parents[1]
DATA = BASE / "data"
IMG_DIR = DATA / "images"
PDF_DIR = DATA / "pdfs"
VID_DIR = DATA / "video"
DATA.mkdir(exist_ok=True, parents=True)
IMG_DIR.mkdir(exist_ok=True, parents=True)
PDF_DIR.mkdir(exist_ok=True, parents=True)
VID_DIR.mkdir(exist_ok=True, parents=True)

def make_sales_excel(fp: pathlib.Path):
    # สร้างข้อมูลยอดขายจำลอง 18 เดือน, 50 ลูกค้า, 10 สินค้า ~1,200 แถว
    start = datetime.today().replace(day=1) - timedelta(days=31*17)
    customers = [f"C{str(i).zfill(3)}" for i in range(1, 51)]
    products  = [f"P{str(i).zfill(2)}"  for i in range(1, 11)]
    rows = []
    oid = 1
    rng = np.random.default_rng(42)
    days = 18*30
    for d in range(days):
        date = start + timedelta(days=d)
        # orders ต่อวันแบบสุ่ม
        for _ in range(rng.integers(5, 15)):
            cust = random.choice(customers)
            prod = random.choice(products)
            qty  = int(max(1, rng.normal(3, 2)))
            price= round(max(10, rng.normal(100, 25)), 2)
            rows.append([date.date(), f"O{oid:06d}", cust, prod, qty, price])
            oid += 1
    df = pd.DataFrame(rows, columns=["date","order_id","customer_id","product_id","quantity","price"])
    fp.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(fp, index=False)
    print(f"[ok] sales.xlsx -> {fp}")

def make_two_images():
    img1 = np.full((250, 400, 3), 230, dtype=np.uint8)
    cv2.putText(img1, "Image A", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv2.rectangle(img1, (60,80), (160,180), (0,0,0), -1)

    img2 = img1.copy()
    cv2.rectangle(img2, (220,90), (320,190), (0,0,255), -1)  # ความต่างเพิ่มเข้ามา
    cv2.imwrite(str(IMG_DIR/"img_a.png"), img1)
    cv2.imwrite(str(IMG_DIR/"img_b.png"), img2)
    print("[ok] images -> data/images/img_a.png, img_b.png")

def make_video():
    path = VID_DIR / "sample.mp4"
    w,h,fps = 320,240,10
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    out = cv2.VideoWriter(str(path), fourcc, fps, (w,h))
    for t in range(60):
        frame = np.full((h,w,3), 255, dtype=np.uint8)
        # เอากล่องแทน "คน" ที่เดินผ่าน (motion detector จะจับได้)
        x = 10 + t*3
        cv2.rectangle(frame, (x,120-20), (x+20,120+20), (0,0,0), -1)
        out.write(frame)
    out.release()
    print(f"[ok] video -> {path}")

def make_two_pdfs():
    def write_pdf(path: pathlib.Path, lines):
        doc = fitz.open()
        page = doc.new_page()
        text = "\n".join(lines)
        rect = fitz.Rect(40, 40, 560, 800)
        page.insert_textbox(rect, text, fontsize=12, fontname="helv")
        doc.save(str(path))
        doc.close()

    a_lines = [
        "INVOICE 1001",
        "Customer: ACME CO.",
        "Date: 2024-11-01",
        "Items:",
        "- Widget A x 3",
        "- Widget B x 2",
        "Total: 500.00"
    ]
    b_lines = [
        "INVOICE 1001",
        "Customer: ACME CORPORATION",
        "Date: 2024-11-02",
        "Items:",
        "- Widget A x 4",
        "- Widget C x 1",
        "Total: 540.00",
        "Notes: deliver ASAP"
    ]
    write_pdf(PDF_DIR/"a.pdf", a_lines)
    write_pdf(PDF_DIR/"b.pdf", b_lines)
    print("[ok] pdf -> data/pdfs/a.pdf, b.pdf")

def main():
    if not (DATA/"sales.xlsx").exists():
        make_sales_excel(DATA/"sales.xlsx")
    make_two_images()
    make_video()
    make_two_pdfs()

if __name__ == "__main__":
    main()

