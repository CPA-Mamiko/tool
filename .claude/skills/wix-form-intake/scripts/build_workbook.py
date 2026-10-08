"""Build the pre-meeting workbook (.xlsx) from a JSON spec.

Usage:
    python3 build_workbook.py spec.json "Smith_Prep_Workbook_20261009.xlsx"

spec.json:
{
  "title": "John Smith – Pre-meeting workbook / 面談準備ワークブック",
  "subtitle": "Meeting 9 Oct 2026 17:00 JST (Zoom) · Prepared 8 Oct 2026",
  "sheets": [
    {
      "name": "1_Overview",                       (max 31 chars, no []:*?/\\)
      "heading": "Overview / 概要",               (optional, row above the table)
      "columns": [{"header": "Item / 項目", "width": 28},
                  {"header": "Detail / 内容", "width": 80}],
      "rows": [["Client / 顧客", "John Smith"], ...],
      "input_columns": [],                         (0-based; shaded yellow for notes during the meeting)
      "group_column": null                         (optional 0-based column; a new value starts a shaded band)
    }
  ]
}

Sheet layout, column choices and content rules: references/workbook-spec.md.
"""
import json
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

FONT = "Meiryo UI"
HEADER_FILL = PatternFill("solid", fgColor="1F3864")
INPUT_FILL = PatternFill("solid", fgColor="FFF8DC")
BAND_FILL = PatternFill("solid", fgColor="EEF2F7")
THIN = Side(style="thin", color="C8CCD2")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")


def build_sheet(ws, spec, title, subtitle):
    ws["A1"] = title
    ws["A1"].font = Font(name=FONT, size=14, bold=True)
    ws["A2"] = subtitle
    ws["A2"].font = Font(name=FONT, size=9, color="555555")
    row = 3
    if spec.get("heading"):
        row += 1
        ws.cell(row=row, column=1, value=spec["heading"]).font = Font(name=FONT, size=12, bold=True)
    row += 1
    header_row = row

    for c, col in enumerate(spec["columns"], start=1):
        cell = ws.cell(row=row, column=c, value=col["header"])
        cell.font = Font(name=FONT, size=10, bold=True, color="FFFFFF")
        cell.fill = HEADER_FILL
        cell.alignment = WRAP
        cell.border = BORDER
        ws.column_dimensions[cell.column_letter].width = col.get("width", 20)

    inputs = set(spec.get("input_columns", []))
    group_col = spec.get("group_column")
    band, last_group = False, object()
    for values in spec["rows"]:
        row += 1
        if group_col is not None and values[group_col] != last_group:
            band, last_group = not band, values[group_col]
        for c in range(len(spec["columns"])):
            value = values[c] if c < len(values) else ""
            cell = ws.cell(row=row, column=c + 1, value=value)
            cell.font = Font(name=FONT, size=10)
            cell.alignment = WRAP
            cell.border = BORDER
            if c in inputs:
                cell.fill = INPUT_FILL
            elif band:
                cell.fill = BAND_FILL

    ws.freeze_panes = ws.cell(row=header_row + 1, column=1)
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = f"{header_row}:{header_row}"


def main(src, dst):
    with open(src, encoding="utf-8") as f:
        spec = json.load(f)
    wb = Workbook()
    wb.remove(wb.active)
    for sheet in spec["sheets"]:
        build_sheet(wb.create_sheet(sheet["name"][:31]), sheet, spec["title"], spec.get("subtitle", ""))
    wb.save(dst)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
