#!/usr/bin/env python3
"""重新產生技術報告 report.pdf。

流程：make_diagrams.py → pandoc（report.md → docx）→ python-docx 後處理 → LibreOffice（docx → pdf）
需要：pandoc、LibreOffice（soffice）、python-docx、matplotlib，以及 Noto Sans CJK TC 字型。
執行：python build_report.py
"""
from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
FONT = "Noto Sans CJK TC"
MONO = "Noto Sans Mono CJK TC"


def run(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, **kw)


def set_font(style, name, size=None, bold=None, italic=None, color=None):
    f = style.font
    f.name = name
    if size:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    if color:
        f.color.rgb = RGBColor.from_string(color)
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rfonts.get(qn(attr)) is not None:
            del rfonts.attrib[qn(attr)]
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), name)


def make_reference_docx(path: pathlib.Path):
    default = BUILD / "default_reference.docx"
    with open(default, "wb") as fh:
        subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"],
                       check=True, stdout=fh)
    doc = Document(default)
    for s in doc.styles:
        try:
            if s.type in (1, 2):  # paragraph / character
                set_font(s, MONO if s.name in ("Verbatim Char", "Source Code") else FONT)
        except Exception:
            pass
    names = {st.name: st for st in doc.styles}

    def sty(n):
        return names.get(n)

    set_font(sty("Normal"), FONT, 10.5)
    for n in ("Body Text", "First Paragraph", "Compact", "Block Text"):
        if sty(n):
            set_font(sty(n), FONT, 10.5 if n != "Compact" else 9.5)
    if sty("Compact"):
        sty("Compact").paragraph_format.space_after = Pt(1)
        sty("Compact").paragraph_format.space_before = Pt(1)
    for n in ("Body Text", "First Paragraph"):
        if sty(n):
            sty(n).paragraph_format.space_after = Pt(6)
            sty(n).paragraph_format.line_spacing = 1.25
    set_font(sty("Title"), FONT, 20, bold=True, color="1F3A5F")
    sty("Title").paragraph_format.space_before = Pt(110)
    sty("Title").paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for n, size in (("Subtitle", 14), ("Author", 12), ("Date", 11)):
        if sty(n):
            set_font(sty(n), FONT, size, color="444444")
            sty(n).paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(sty("Heading 1"), FONT, 17, bold=True, color="1F3A5F")
    sty("Heading 1").paragraph_format.page_break_before = True
    sty("Heading 1").paragraph_format.space_after = Pt(8)
    set_font(sty("Heading 2"), FONT, 13, bold=True, color="2F5D8A")
    set_font(sty("Heading 3"), FONT, 11.5, bold=True, color="2F5D8A")
    if sty("Heading 4"):
        set_font(sty("Heading 4"), FONT, 10.5, bold=True, color="2F5D8A")
        sty("Heading 4").paragraph_format.space_before = Pt(10)
    if sty("Hyperlink"):
        set_font(sty("Hyperlink"), FONT, color="0563C1")
        sty("Hyperlink").font.underline = True
    for n in ("Image Caption", "Captioned Figure", "Figure"):
        if sty(n):
            sty(n).paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if sty("Image Caption"):
        set_font(sty("Image Caption"), FONT, 9.5, italic=False, color="444444")
    if sty("Source Code"):
        set_font(sty("Source Code"), MONO, 8.5)
    if sty("Verbatim Char"):
        set_font(sty("Verbatim Char"), MONO, 9)
    for section in doc.sections:
        section.page_width, section.page_height = Cm(21.0), Cm(29.7)
        section.left_margin = section.right_margin = Cm(2.2)
        section.top_margin, section.bottom_margin = Cm(2.2), Cm(2.2)
    doc.save(path)


def add_borders(tbl):
    tblPr = tbl._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "A6A6A6")
        borders.append(el)
    tblPr.append(borders)


def shade(element_pr, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    element_pr.append(shd)


def add_page_number(section):
    p = section.footer.paragraphs[0] if section.footer.paragraphs else section.footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_ = p.add_run()
    for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tag)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run_._r.append(el)
    run_.font.size = Pt(9)


TEXT_WIDTH_TWIPS = 9412  # A4 寬 11906 − 左右邊界各 1247


def _visual_len(text: str) -> int:
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in text)


def fit_tables(doc):
    """所有表格固定為文字區寬度；沒有欄寬的表格依內容長度分配；長字串可在 _ / . - 處換行。"""
    for tbl in doc.tables:
        n = len(tbl.rows[0].cells)
        grid_el = tbl._tbl.tblGrid
        grid = [int(g.get(qn("w:w"))) for g in grid_el.findall(qn("w:gridCol"))]
        if len(grid) == n and sum(grid) > 0:
            weights = grid
        else:
            weights = []
            for ci in range(n):
                longest = max(_visual_len(row.cells[ci].text) for row in tbl.rows)
                weights.append(min(max(longest, 6), 40))
        total = sum(weights)
        widths = [round(TEXT_WIDTH_TWIPS * w / total) for w in weights]
        widths[-1] += TEXT_WIDTH_TWIPS - sum(widths)

        tblPr = tbl._tbl.tblPr
        for tag in ("w:tblW", "w:tblLayout"):
            for el in tblPr.findall(qn(tag)):
                tblPr.remove(el)
        tw = OxmlElement("w:tblW")
        tw.set(qn("w:w"), str(TEXT_WIDTH_TWIPS))
        tw.set(qn("w:type"), "dxa")
        tblPr.append(tw)
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        tblPr.append(layout)

        for g in list(grid_el):
            grid_el.remove(g)
        for w in widths:
            gc = OxmlElement("w:gridCol")
            gc.set(qn("w:w"), str(w))
            grid_el.append(gc)
        for row in tbl.rows:
            for ci, cell in enumerate(row.cells):
                tcPr = cell._tc.get_or_add_tcPr()
                for el in tcPr.findall(qn("w:tcW")):
                    tcPr.remove(el)
                tcw = OxmlElement("w:tcW")
                tcw.set(qn("w:w"), str(widths[ci]))
                tcw.set(qn("w:type"), "dxa")
                tcPr.insert(0, tcw)

        for t_el in tbl._tbl.iter(qn("w:t")):
            text = t_el.text or ""
            if any(len(tok) > 24 for tok in text.split()) or len(text) > 24 and " " not in text:
                t_el.text = re.sub(r"([_/.\-])(?=[A-Za-z0-9])", "\\1\u200b", text)
                t_el.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def postprocess(src: pathlib.Path, dst: pathlib.Path, headings=None, pages=None) -> int:
    doc = Document(src)
    fit_tables(doc)
    if headings:
        insert_toc(doc, headings, pages)
    for tbl in doc.tables:
        add_borders(tbl)
        for ri, row in enumerate(tbl.rows):
            for cell in row.cells:
                if ri == 0:
                    shade(cell._tc.get_or_add_tcPr(), "E8EEF4")
                    for para in cell.paragraphs:
                        for r in para.runs:
                            r.bold = True
    placeholders = 0
    for para in doc.paragraphs:
        if para.style is not None and para.style.name == "Source Code":
            shade(para._p.get_or_add_pPr(), "F3F5F7")
        if "【待補" in para.text:
            placeholders += 1
            shade(para._p.get_or_add_pPr(), "FFF2CC")
        if para._p.xpath(".//w:drawing"):
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if "【待補" in para.text:
                        placeholders += 1
                        shade(cell._tc.get_or_add_tcPr(), "FFF2CC")
    for section in doc.sections:
        add_page_number(section)
    doc.save(dst)
    return placeholders

# ---------------------------------------------------------------- 目錄（含頁碼）
def parse_headings(md_text: str):
    """取出 report.md 的 H1、H2 標題（略過 YAML 前言、程式碼區塊與「目錄」本身）。"""
    body = md_text.split("\n---\n", 1)[1] if md_text.startswith("---") else md_text
    heads, in_code = [], False
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"(#{1,2}) (.+?)\s*$", line)
        if m:
            text = m.group(2).replace("{-}", "").strip()
            if re.sub(r"[\s　]+", "", text) == "目錄":
                continue
            heads.append((len(m.group(1)), text))
    return heads


def _squash(s: str) -> str:
    return re.sub(r"[\s　​]+", "", s)


def find_pages(pdf: pathlib.Path, headings, start_page: int = 3):
    """在 PDF 中依序找出每個標題所在頁（目錄頁之後；頁碼從 1 起算，與頁尾頁碼一致）。"""
    out = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    texts = [_squash(t) for t in out.split("\f")]
    pages, cur = [], start_page
    for _level, text in headings:
        key_full = _squash(text)
        key_title = _squash(re.sub(r"^[\d.]+", "", text))   # 不含編號（標題旁若緊接清單，編號與標題可能被拆開）
        found = None
        for key in (key_full, key_title):
            for i in range(cur, len(texts) + 1):
                if key and key in texts[i - 1]:
                    found = i
                    break
            if found:
                break
        if found:
            cur = found
        pages.append(found)
    return pages


def insert_toc(doc, headings, pages):
    marker = next((p for p in doc.paragraphs if p.text.strip() == "{{TOC}}"), None)
    if marker is None:
        return
    for (level, text), pg in zip(headings, pages):
        para = marker.insert_paragraph_before()
        pf = para.paragraph_format
        pf.tab_stops.add_tab_stop(Cm(16.6), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        pf.left_indent = Cm(0 if level == 1 else 0.9)
        pf.space_before = Pt(8 if level == 1 else 1)
        pf.space_after = Pt(1)
        run_ = para.add_run(f"{text}\t{pg if pg else ''}")
        run_.bold = level == 1
        run_.font.size = Pt(11.5 if level == 1 else 10)
    marker._element.getparent().remove(marker._element)


def convert_to_pdf(docx_path: pathlib.Path) -> pathlib.Path:
    """LibreOffice 的設定檔與輸出放在系統暫存目錄（寫入專案資料夾可能失敗）。"""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="report_pdf_"))
    shutil.copy(docx_path, tmp / "report.docx")
    env = dict(os.environ, HOME=str(tmp))
    run(["soffice", f"-env:UserInstallation=file://{tmp}/lo_profile", "--headless",
         "--convert-to", "pdf", "--outdir", str(tmp), str(tmp / "report.docx")], env=env)
    out = BUILD / "report.pdf"
    shutil.copy(tmp / "report.pdf", out)
    shutil.rmtree(tmp, ignore_errors=True)
    return out


# ---------------------------------------------------------------- 由原稿自動產生的內容
REPO = HERE.parents[1]
PURPOSE = {
    "streamlit": "互動式網頁介面（本專案的 UI 框架）",
    "numpy": "陣列運算：卷積、色彩轉換、直方圖、PSNR",
    "opencv-python-headless": "Haar-Cascade 人臉偵測與邊界框繪製（無 GUI 版本，適合雲端）",
    "pillow": "影像解碼（PNG／JPG／BMP）、EXIF 方向處理",
    "matplotlib": "直方圖繪製",
    "altair": "宣告式圖表（Streamlit 圖表元件）",
    "anyio": "非同步 I/O 抽象層",
    "attrs": "類別屬性定義輔助",
    "certifi": "HTTPS 憑證根清單",
    "charset-normalizer": "文字編碼偵測",
    "click": "命令列介面工具",
    "contourpy": "等高線計算（Matplotlib）",
    "cycler": "繪圖樣式循環（Matplotlib）",
    "fonttools": "字型讀取與處理（Matplotlib）",
    "h11": "HTTP/1.1 協定實作",
    "idna": "國際化網域名稱處理",
    "itsdangerous": "資料簽章",
    "jinja2": "範本引擎",
    "jsonschema": "JSON 結構驗證",
    "jsonschema-specifications": "JSON Schema 規格資料",
    "kiwisolver": "約束求解（Matplotlib 版面配置）",
    "markupsafe": "範本字串跳脫",
    "narwhals": "資料框相容層",
    "packaging": "版本字串解析",
    "pandas": "表格資料處理（Streamlit 表格顯示）",
    "protobuf": "序列化格式（Streamlit 前後端通訊）",
    "pyarrow": "欄式資料格式（Streamlit 資料傳輸）",
    "pydeck": "地圖視覺化（Streamlit）",
    "pyparsing": "文字剖析（Matplotlib）",
    "python-dateutil": "日期時間處理",
    "python-multipart": "表單與檔案上傳解析",
    "referencing": "JSON 參照解析",
    "requests": "HTTP 用戶端",
    "rpds-py": "持久性資料結構",
    "starlette": "ASGI 網頁框架（Streamlit 伺服器）",
    "typing-extensions": "型別提示向後相容",
    "tzdata": "時區資料",
    "urllib3": "HTTP 連線函式庫",
    "uvicorn": "ASGI 伺服器",
    "watchdog": "檔案變更監看",
    "websockets": "WebSocket 實作",
}


def build_req_table() -> str:
    items, cur = [], None
    for ln in (REPO / "requirements.txt").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Za-z0-9_.\-]+)==([^\s;]+)", ln)
        if m:
            cur = [m.group(1), m.group(2), []]
            items.append(cur)
            continue
        s = ln.strip()
        if cur is not None and ln.startswith((" ", "\t")) and s.startswith("#"):
            if s.startswith("# via"):
                rest = s[5:].strip()
                if rest:
                    cur[2].append(rest)
            else:
                cur[2].append(s.lstrip("#").strip())
    missing = [n for n, _v, _w in items if n.lower() not in PURPOSE]
    if missing:
        raise SystemExit(f"requirements.txt 有套件缺少用途說明：{missing}")
    rows = ["| 套件 | 版本 | 類型 | 被誰需要 | 用途 |", "|:--------------------|:----------|:----|:------------------|:--------------------------------|"]
    for name, ver, via in sorted(items, key=lambda x: x[0].lower()):
        direct = "dip-mid" in via
        others = [v for v in via if v != "dip-mid"]
        need = ("本專案" + ("、" + "、".join(others[:2]) + ("…" if len(others) > 2 else "") if others else "")) if direct \
            else "、".join(others[:3]) + ("…" if len(others) > 3 else "")
        rows.append(f"| `{name}` | {ver} | {'**直接**' if direct else '間接'} | {need} | {PURPOSE[name.lower()]} |")
    print(f"套件表：{len(items)} 條（直接 {sum('dip-mid' in i[2] for i in items)}）")
    return "\n".join(rows)


STAGES = [
    ("階段 1　需求分析、規劃與環境建置（P1–P4）", "01_project_setup.md"),
    ("階段 2　影像載入與色彩空間（P5–P6）", "02_io_and_color.md"),
    ("階段 3　卷積濾波與 PSNR（P6–P8）", "03_filtering_psnr.md"),
    ("階段 4　人臉偵測（P8）", "04_face_detection.md"),
    ("階段 5　README、GitHub 與部署（P9–P14）", "05_git_deployment.md"),
    ("階段 6　報告、補件與繳交前檢查（P15–P28）", "06_report_and_colab.md"),
]


def convert_log(text: str) -> str:
    text = text.replace("【待補】", "「待補」標記")   # 歷程中描述過去待補項目的文字，避免被誤標為未完成
    out, in_code = [], False
    for ln in text.splitlines():
        if ln.strip().startswith("```"):
            in_code = not in_code
            out.append(ln)
            continue
        if in_code:
            out.append(ln)
            continue
        if ln.startswith("# ") or ln.strip() == "---":
            continue                                   # 檔案標題（改用階段標題）與水平線
        if ln.startswith("## 待記錄"):
            break                                      # 其後為待辦說明，不納入
        if ln.startswith("## "):
            out.append("#### " + ln[3:])
        elif ln.startswith("### "):
            out.append("**" + ln[4:].strip() + "**")
        else:
            out.append(re.sub(r"\[([^\]]+)\]\(([^)]*\.md)\)", r"\1", ln))
    return "\n".join(out)


def build_audit_trail() -> str:
    parts = []
    for title, fname in STAGES:
        body = convert_log((REPO / "prompt_log" / fname).read_text(encoding="utf-8"))
        parts.append(f"### {title}\n\n{body}\n")
    return "\n".join(parts)


def assemble_markdown() -> pathlib.Path:
    text = (HERE / "report.md").read_text(encoding="utf-8")
    text = text.replace("{{REQ_TABLE}}", build_req_table()).replace("{{AUDIT_TRAIL}}", build_audit_trail())
    full = BUILD / "report_full.md"
    full.write_text(text, encoding="utf-8")
    return full


def submission_name() -> str:
    m = re.search(r'author:\s*"(\S+?)[　\s]+(C\d+)"', (HERE / "report.md").read_text(encoding="utf-8"))
    return f"{m.group(2)}_{m.group(1)}_期中專題.pdf" if m else "report_submission.pdf"


def main():
    BUILD.mkdir(exist_ok=True)
    run([sys.executable, str(HERE / "make_diagrams.py")])
    ref = BUILD / "reference.docx"
    make_reference_docx(ref)
    raw = BUILD / "report_raw.docx"
    full = assemble_markdown()
    run(["pandoc", str(full), "-f", "markdown", "-o", str(raw),
         "--reference-doc", str(ref), "--resource-path", str(HERE)])
    headings = parse_headings(full.read_text(encoding="utf-8"))
    pages = [None] * len(headings)          # 第一輪先留空，取得實際頁碼後再填入
    final = BUILD / "report.docx"
    pdf = None
    for attempt in range(1, 5):
        n = postprocess(raw, final, headings, pages)
        pdf = convert_to_pdf(final)
        found = find_pages(pdf, headings)
        print(f"第 {attempt} 輪：目錄頁碼{'已穩定' if found == pages else '更新'} {found}")
        if found == pages:
            break
        pages = found
    else:
        raise SystemExit("目錄頁碼未收斂，請檢查版面。")
    missing = [h for h, pg in zip(headings, pages) if pg is None]
    if missing:
        raise SystemExit(f"找不到這些標題所在頁：{missing}")
    shutil.copy(pdf, HERE / "report.pdf")
    shutil.copy(pdf, HERE / submission_name())
    print(f"完成：{HERE / 'report.pdf'}（待補標記 {n} 處，目錄 {len(headings)} 條）")


if __name__ == "__main__":
    main()
