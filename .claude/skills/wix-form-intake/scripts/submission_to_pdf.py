"""Render a Wix form submission as a PDF (Japanese and English text supported).

Usage:
    python3 submission_to_pdf.py submission.json "Personal information_John Smith.pdf"

submission.json:
{
  "form_name": "Personal information ／基本情報（個人）",
  "submitted_at": "2026-10-07 17:04 JST",
  "submission_id": "812e0df1-...",            (optional)
  "fields": [
    {"label": "First Name／名", "value": "John"},
    {"label": "Birth date ／生年月日", "value": "1994-07-11"},
    {"label": "Passport", "value": null, "note": "添付ファイルあり: passport.pdf"}
  ]
}

Empty values (null, "", []) are printed as "（未回答）". Lists are joined with ", ".
"""
import glob
import json
import os
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Embedded TrueType fonts that cover Japanese (Linux, Windows, macOS). The first one found is used.
# The built-in CID font is the last resort: it is not embedded, so viewers without a
# Japanese language pack cannot show it.
FONT_CANDIDATES = [
    ("/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf", None),
    ("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", None),
    ("/usr/share/fonts/opentype/ipaexfont-gothic/ipaexg.ttf", None),
    ("C:/Windows/Fonts/meiryo.ttc", 0),
    ("C:/Windows/Fonts/msgothic.ttc", 0),
    ("C:/Windows/Fonts/YuGothM.ttc", 0),
    ("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", 0),
    ("/Library/Fonts/Arial Unicode.ttf", None),
]


def register_font():
    paths = FONT_CANDIDATES + [(p, None) for p in glob.glob("/usr/share/fonts/**/ipag*.ttf", recursive=True)]
    for path, index in paths:
        if not os.path.exists(path):
            continue
        try:
            kwargs = {"subfontIndex": index} if index is not None else {}
            pdfmetrics.registerFont(TTFont("JP", path, **kwargs))
            return "JP"
        except Exception:
            continue
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
    print("warning: no embeddable Japanese font found; using non-embedded CID font", file=sys.stderr)
    return "HeiseiKakuGo-W5"


FONT = register_font()

TITLE = ParagraphStyle("title", fontName=FONT, fontSize=15, leading=20, spaceAfter=4)
META = ParagraphStyle("meta", fontName=FONT, fontSize=8.5, leading=12, textColor=colors.HexColor("#555555"))
LABEL = ParagraphStyle("label", fontName=FONT, fontSize=9, leading=13)
VALUE = ParagraphStyle("value", fontName=FONT, fontSize=10, leading=14)
NOTE = ParagraphStyle("note", fontName=FONT, fontSize=8, leading=11, textColor=colors.HexColor("#8a4b00"))


def text(value):
    if value is None or value == "" or value == []:
        return "（未回答）"
    if isinstance(value, list):
        return ", ".join(text(v) for v in value)
    if isinstance(value, dict):
        return ", ".join(f"{k}: {text(v)}" for k, v in value.items())
    return str(value)


def para(value, style):
    return Paragraph(escape(value).replace("\n", "<br/>"), style)


def main(src, dst):
    with open(src, encoding="utf-8") as f:
        data = json.load(f)

    story = [para(data["form_name"], TITLE)]
    meta = [f"Submitted / 受信日時: {data.get('submitted_at', '')}"]
    if data.get("submission_id"):
        meta.append(f"Submission ID: {data['submission_id']}")
    story += [para("　".join(meta), META), Spacer(1, 6 * mm)]

    rows = []
    for field in data["fields"]:
        cell = [para(text(field.get("value")), VALUE)]
        if field.get("note"):
            cell.append(para(field["note"], NOTE))
        rows.append([para(field["label"], LABEL), cell])

    table = Table(rows, colWidths=[62 * mm, 112 * mm], repeatRows=0)
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f2f4f7")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c8ccd2")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(table)

    doc = SimpleDocTemplate(dst, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm,
                            title=data["form_name"], author="Tokyo Advisory")
    doc.build(story)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
