import subprocess, sys, pathlib

BASE = pathlib.Path(__file__).resolve().parent
def py(args): 
    subprocess.check_call([sys.executable] + args, cwd=str(BASE))

def main():
    # 1) เตรียมข้อมูลตัวอย่าง (ถ้าไม่มี)
    py(["scripts/generate_sample_data.py"])
    # 2) Analytics
    py(["scripts/pipeline_sales.py"])
    # 3) Vision (image diff + video detection)
    py(["scripts/pipeline_vision.py"])
    # 4) PDF diff
    py(["scripts/pipeline_pdfdiff.py"])
    print("\nAll done. JSON files are in ./dist")

if __name__ == "__main__":
    main()
