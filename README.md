# malee-DataScience-OCR

ได้ไฟล์ JSON อะไรบ้าง?

dist/sales_analysis.json

monthly_sales[]: ยอดขายต่อเดือน (ยอดจำลอง)

demand_forecast[]: คาดการณ์จำนวนสั่งซื้อรายสินค้าเดือนถัดไป (moving average 3 เดือน)

rfm_segments[]: จำนวนลูกค้าต่อคลัสเตอร์ + ค่าเฉลี่ย R/F/M + top customers

dist/vision_results.json

image_diff: คะแนน SSIM และกรอบตำแหน่งที่แตกต่างระหว่างรูป A/B

video_detection: เวลาที่พบ “คน” (ถ้าตรวจได้จาก HOG) หรืออย่างน้อย “การเคลื่อนไหว” จาก motion detector

dist/pdf_diff.json

line_diffs[]: บล็อกบรรทัดที่เพิ่ม/หาย/แก้ พร้อมเลขหน้า-เลขบรรทัด

word_delta: คำที่เพิ่ม/หายโดยรวม

โค้ดทั้งหมดวิ่งได้บน GitHub Actions เลยเพราะสคริปต์สร้างข้อมูลตัวอย่างเอง (Excel/ภาพ/วิดีโอ/PDF)
