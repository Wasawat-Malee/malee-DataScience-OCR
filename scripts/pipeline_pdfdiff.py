import json, pathlib, fitz, re, difflib
from collections import Counter

BASE = pathlib.Path(__file__).resolve().parents[1]
PDF_A = BASE / "data" / "pdfs" / "a.pdf"
PDF_B = BASE / "data" / "pdfs" / "b.pdf"
DIST  = BASE / "dist"
DIST.mkdir(exist_ok=True, parents=True)

def pdf_lines(path: pathlib.Path):
    doc = fitz.open(str(path))
    lines = []
    for pi, p in enumerate(doc, start=1):
        text = p.get_text("text")
        for li, line in enumerate(text.splitlines(), start=1):
            # normalise whitespace
            line = re.sub(r"\s+", " ", line.strip())
            lines.append((pi, li, line))
    doc.close()
    return lines

def line_blocks_diff(a_lines, b_lines):
    # ใช้ SequenceMatcher ระบุช่วงบรรทัดที่เปลี่ยน (insert/delete/replace)
    a_texts = [l[2] for l in a_lines]
    b_texts = [l[2] for l in b_lines]
    sm = difflib.SequenceMatcher(a=a_texts, b=b_texts)
    blocks = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal": 
            continue
        block = {
            "tag": tag,
            "a_range": [i1+1, i2],   # index -> human 1-based
            "b_range": [j1+1, j2],
            "a_excerpt": [{"page": a_lines[i][0], "line": a_lines[i][1], "text": a_lines[i][2]} for i in range(i1, i2)],
            "b_excerpt": [{"page": b_lines[j][0], "line": b_lines[j][1], "text": b_lines[j][2]} for j in range(j1, j2)]
        }
        blocks.append(block)
    return blocks

def word_delta(a_lines, b_lines):
    tok = lambda s: re.findall(r"[A-Za-z0-9_.-]+", s.lower())
    wa = Counter(w for _,_,l in a_lines for w in tok(l))
    wb = Counter(w for _,_,l in b_lines for w in tok(l))
    added   = sorted((set(wb) - set(wa)))
    removed = sorted((set(wa) - set(wb)))
    return {"added_words": added[:100], "removed_words": removed[:100]}

def run():
    a = pdf_lines(PDF_A)
    b = pdf_lines(PDF_B)
    out = {
        "a_path": str(PDF_A).replace(str(BASE)+"/", ""),
        "b_path": str(PDF_B).replace(str(BASE)+"/", ""),
        "line_diffs": line_blocks_diff(a,b),
        "word_delta": word_delta(a,b)
    }
    (DIST/"pdf_diff.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[ok] dist/pdf_diff.json")

if __name__ == "__main__":
    run()
