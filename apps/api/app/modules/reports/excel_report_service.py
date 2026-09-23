import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import xlsxwriter


class ExcelReportBuilder:
    """
    Standardized multi-sheet Excel spreadsheet generator for Project PRAGYA.
    Produces formatted, audit-compliant workbooks with dedicated executive overview,
    structured data tables, and methodology audit worksheets.
    """

    def __init__(self, workbook_title: str):
        self.output = io.BytesIO()
        self.workbook = xlsxwriter.Workbook(self.output, {"in_memory": True})
        self.workbook_title = workbook_title

        # Initialize reusable styles
        self.fmt_title = self.workbook.add_format({
            "bold": True,
            "font_size": 14,
            "font_color": "#FFFFFF",
            "bg_color": "#0F172A",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#334155",
        })
        self.fmt_subtitle = self.workbook.add_format({
            "font_size": 9,
            "font_color": "#64748B",
            "italic": True,
        })
        self.fmt_meta_label = self.workbook.add_format({
            "bold": True,
            "font_size": 9,
            "font_color": "#334155",
            "bg_color": "#F1F5F9",
            "border": 1,
            "border_color": "#CBD5E1",
        })
        self.fmt_meta_val = self.workbook.add_format({
            "font_size": 9,
            "font_color": "#0F172A",
            "bg_color": "#FFFFFF",
            "border": 1,
            "border_color": "#CBD5E1",
        })
        self.fmt_header = self.workbook.add_format({
            "bold": True,
            "font_size": 10,
            "font_color": "#FFFFFF",
            "bg_color": "#1E293B",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#334155",
        })
        self.fmt_cell = self.workbook.add_format({
            "font_size": 9,
            "font_color": "#1E293B",
            "border": 1,
            "border_color": "#E2E8F0",
            "valign": "vcenter",
        })
        self.fmt_cell_zebra = self.workbook.add_format({
            "font_size": 9,
            "font_color": "#1E293B",
            "bg_color": "#F8FAFC",
            "border": 1,
            "border_color": "#E2E8F0",
            "valign": "vcenter",
        })
        self.fmt_num = self.workbook.add_format({
            "font_size": 9,
            "font_color": "#1E293B",
            "border": 1,
            "border_color": "#E2E8F0",
            "num_format": "0.0",
            "valign": "vcenter",
        })
        self.fmt_pct = self.workbook.add_format({
            "font_size": 9,
            "font_color": "#1E293B",
            "border": 1,
            "border_color": "#E2E8F0",
            "num_format": "0.0%",
            "valign": "vcenter",
        })

    def add_summary_sheet(
        self,
        sheet_name: str,
        title: str,
        kpis: List[Tuple[str, Any, str]],
        summary_text: str,
        metadata: Optional[Dict[str, str]] = None,
    ):
        ws = self.workbook.add_worksheet(sheet_name[:31])
        ws.set_column("A:A", 22)
        ws.set_column("B:B", 30)
        ws.set_column("C:C", 25)
        ws.set_column("D:D", 25)

        # Title Row
        ws.merge_range("A1:D1", f"PRAGYA: {title.upper()}", self.fmt_title)
        ws.set_row(0, 30)

        ws.write("A2", "Official Statistical Cadre Competency Intelligence System", self.fmt_subtitle)

        # Metadata table
        row = 3
        meta = metadata or {}
        meta_items = [
            ("Report Type", title),
            ("Generated At", meta.get("Generated", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))),
            ("Audit Scope", meta.get("Scope", "National Statistical Cadre")),
            ("Data Quality", meta.get("Data Quality", "SUFFICIENT (HIGH)")),
            ("Specification", "PRAGYA v1.0 Statutory Cadre Review Benchmark"),
        ]
        for k, v in meta_items:
            ws.write(row, 0, k, self.fmt_meta_label)
            ws.write(row, 1, v, self.fmt_meta_val)
            row += 1

        row += 1
        # Executive Summary Paragraph
        ws.write(row, 0, "EXECUTIVE SUMMARY", self.fmt_meta_label)
        ws.merge_range(row, 1, row + 1, 3, summary_text, self.fmt_cell)
        row += 3

        # KPI Tiles
        ws.write(row, 0, "PRIMARY CADRE CAPACITY BENCHMARKS", self.fmt_header)
        ws.write(row, 1, "METRIC VALUE", self.fmt_header)
        ws.write(row, 2, "CONTEXT / BENCHMARK", self.fmt_header)
        row += 1

        for label, val, ctx in kpis:
            ws.write(row, 0, label, self.fmt_cell)
            ws.write(row, 1, str(val), self.fmt_cell)
            ws.write(row, 2, ctx, self.fmt_cell)
            row += 1

    def add_data_sheet(
        self,
        sheet_name: str,
        headers: List[str],
        rows: List[List[Any]],
        col_widths: Optional[List[int]] = None,
    ):
        ws = self.workbook.add_worksheet(sheet_name[:31])
        ws.set_row(0, 24)

        if col_widths:
            for idx, w in enumerate(col_widths):
                col_letter = chr(65 + idx) if idx < 26 else "Z"
                ws.set_column(f"{col_letter}:{col_letter}", w)
        else:
            for idx in range(len(headers)):
                col_letter = chr(65 + idx) if idx < 26 else "Z"
                ws.set_column(f"{col_letter}:{col_letter}", 18)

        # Header
        for c_idx, h in enumerate(headers):
            ws.write(0, c_idx, str(h).upper(), self.fmt_header)

        # Rows
        for r_idx, row in enumerate(rows):
            style = self.fmt_cell_zebra if (r_idx % 2 == 1) else self.fmt_cell
            for c_idx, val in enumerate(row):
                if isinstance(val, float):
                    ws.write_number(r_idx + 1, c_idx, val, self.fmt_num)
                elif isinstance(val, int):
                    ws.write_number(r_idx + 1, c_idx, val, style)
                else:
                    ws.write_string(r_idx + 1, c_idx, str(val if val is not None else "—"), style)

    def add_audit_methodology_sheet(
        self,
        methodology_text: str,
        source_tables: List[str],
        assumptions: List[str],
    ):
        ws = self.workbook.add_worksheet("Audit & Methodology")
        ws.set_column("A:A", 25)
        ws.set_column("B:B", 60)

        ws.merge_range("A1:B1", "PRAGYA AUDIT TRACEABILITY & GOVERNANCE METHODOLOGY", self.fmt_title)
        ws.set_row(0, 28)

        row = 3
        ws.write(row, 0, "Analytical Engine", self.fmt_meta_label)
        ws.write(row, 1, "Deterministic Multi-Factor Cadre Capacity Model (Stages 13-17)", self.fmt_meta_val)
        row += 1

        ws.write(row, 0, "Methodology Overview", self.fmt_meta_label)
        ws.write(row, 1, methodology_text, self.fmt_meta_val)
        row += 2

        ws.write(row, 0, "SOURCE TABLES", self.fmt_header)
        ws.write(row, 1, "DOMAIN / USAGE DESCRIPTION", self.fmt_header)
        row += 1

        for tbl in source_tables:
            ws.write(row, 0, tbl, self.fmt_cell)
            ws.write(row, 1, f"Authoritative PostgreSQL relation for {tbl}", self.fmt_cell)
            row += 1

        row += 1
        ws.write(row, 0, "STATUTORY ASSUMPTIONS", self.fmt_header)
        ws.write(row, 1, "GOVERNANCE POLICY", self.fmt_header)
        row += 1

        for a in assumptions:
            ws.write(row, 0, "Governance Rule", self.fmt_cell)
            ws.write(row, 1, a, self.fmt_cell)
            row += 1

    def finalize(self) -> bytes:
        self.workbook.close()
        self.output.seek(0)
        return self.output.getvalue()
