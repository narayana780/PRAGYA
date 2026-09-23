from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import pymupdf


class PdfReportBuilder:
    """
    Standardized, multi-page PDF document generator for Project PRAGYA.
    Produces high-fidelity, audit-compliant documents with structured headers,
    executive KPI tiles, tabular benchmarks, and governance methodology.
    """

    PAGE_WIDTH = 595.32  # Standard A4 width in points
    PAGE_HEIGHT = 841.92  # Standard A4 height in points
    MARGIN_LEFT = 40.0
    MARGIN_RIGHT = 40.0
    MARGIN_TOP = 40.0
    MARGIN_BOTTOM = 45.0
    CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

    def __init__(self, report_title: str, subtitle: str, metadata: Optional[Dict[str, str]] = None):
        self.report_title = report_title
        self.subtitle = subtitle
        self.metadata = metadata or {}
        self.doc = pymupdf.open()
        self.current_page = None
        self.cursor_y = self.MARGIN_TOP
        self._new_page()

    def _new_page(self):
        self.current_page = self.doc.new_page(width=self.PAGE_WIDTH, height=self.PAGE_HEIGHT)
        self.cursor_y = self.MARGIN_TOP
        self._draw_page_header_banner()

    def _draw_page_header_banner(self):
        page = self.current_page
        if len(self.doc) == 1:
            # First page: Full decorative executive header banner
            banner_rect = pymupdf.Rect(self.MARGIN_LEFT, self.cursor_y, self.PAGE_WIDTH - self.MARGIN_RIGHT, self.cursor_y + 65.0)
            page.draw_rect(banner_rect, color=(0.06, 0.09, 0.16), fill=(0.06, 0.09, 0.16))

            # Left accent bar
            accent_rect = pymupdf.Rect(self.MARGIN_LEFT, self.cursor_y, self.MARGIN_LEFT + 4.0, self.cursor_y + 65.0)
            page.draw_rect(accent_rect, color=(0.02, 0.71, 0.83), fill=(0.02, 0.71, 0.83))

            # Title text
            page.insert_text((self.MARGIN_LEFT + 14.0, self.cursor_y + 24.0), "PRAGYA WORKFORCE INTELLIGENCE REPORT", fontsize=9.0, fontname="helv", color=(0.02, 0.71, 0.83))
            page.insert_text((self.MARGIN_LEFT + 14.0, self.cursor_y + 44.0), self.report_title[:55], fontsize=15.0, fontname="hebo", color=(1.0, 1.0, 1.0))
            page.insert_text((self.MARGIN_LEFT + 14.0, self.cursor_y + 57.0), self.subtitle[:80], fontsize=8.5, fontname="helv", color=(0.8, 0.85, 0.9))

            self.cursor_y += 75.0

            # Metadata Strip
            meta_rect = pymupdf.Rect(self.MARGIN_LEFT, self.cursor_y, self.PAGE_WIDTH - self.MARGIN_RIGHT, self.cursor_y + 22.0)
            page.draw_rect(meta_rect, color=(0.93, 0.95, 0.98), fill=(0.93, 0.95, 0.98))

            ts = self.metadata.get("Generated", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
            scope = self.metadata.get("Scope", "National Statistical Cadre")
            dq = self.metadata.get("Data Quality", "SUFFICIENT (HIGH)")
            ver = self.metadata.get("Version", "v1.0-audit")

            meta_str = f"Generated: {ts}   |   Scope: {scope}   |   Data Quality: {dq}   |   Report Version: {ver}"
            page.insert_text((self.MARGIN_LEFT + 8.0, self.cursor_y + 14.0), meta_str, fontsize=7.5, fontname="helv", color=(0.2, 0.25, 0.35))

            self.cursor_y += 32.0
        else:
            # Continuation page header
            page.insert_text((self.MARGIN_LEFT, self.cursor_y + 10.0), f"PRAGYA: {self.report_title} (Continuation)", fontsize=8.5, fontname="hebo", color=(0.3, 0.35, 0.45))
            page.draw_line(pymupdf.Point(self.MARGIN_LEFT, self.cursor_y + 15.0), pymupdf.Point(self.PAGE_WIDTH - self.MARGIN_RIGHT, self.cursor_y + 15.0), color=(0.85, 0.88, 0.92), width=0.75)
            self.cursor_y += 26.0

    def add_section_heading(self, text: str):
        if self.cursor_y + 30.0 > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
            self._new_page()

        accent_rect = pymupdf.Rect(self.MARGIN_LEFT, self.cursor_y + 2.0, self.MARGIN_LEFT + 3.0, self.cursor_y + 14.0)
        self.current_page.draw_rect(accent_rect, color=(0.02, 0.71, 0.83), fill=(0.02, 0.71, 0.83))

        self.current_page.insert_text(
            (self.MARGIN_LEFT + 8.0, self.cursor_y + 12.0),
            text.upper(),
            fontsize=10.0,
            fontname="hebo",
            color=(0.1, 0.15, 0.25),
        )
        self.cursor_y += 22.0

    def add_kpi_grid(self, metrics: List[Tuple[str, str, str]]):
        """Draws up to 4 metric boxes in a horizontal row."""
        if self.cursor_y + 55.0 > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
            self._new_page()

        count = min(4, len(metrics))
        box_width = (self.CONTENT_WIDTH - ((count - 1) * 8.0)) / count
        box_height = 48.0

        for idx, (label, value, subtext) in enumerate(metrics[:count]):
            box_x = self.MARGIN_LEFT + idx * (box_width + 8.0)
            rect = pymupdf.Rect(box_x, self.cursor_y, box_x + box_width, self.cursor_y + box_height)
            self.current_page.draw_rect(rect, color=(0.88, 0.91, 0.95), fill=(0.97, 0.98, 1.0), width=0.75)

            # Top accent line
            top_line = pymupdf.Rect(box_x, self.cursor_y, box_x + box_width, self.cursor_y + 2.5)
            self.current_page.draw_rect(top_line, color=(0.02, 0.71, 0.83), fill=(0.02, 0.71, 0.83))

            self.current_page.insert_text((box_x + 8.0, self.cursor_y + 14.0), label.upper()[:24], fontsize=7.5, fontname="hebo", color=(0.35, 0.4, 0.5))
            self.current_page.insert_text((box_x + 8.0, self.cursor_y + 31.0), str(value)[:18], fontsize=13.0, fontname="hebo", color=(0.05, 0.1, 0.2))
            self.current_page.insert_text((box_x + 8.0, self.cursor_y + 42.0), subtext[:28], fontsize=7.0, fontname="helv", color=(0.4, 0.5, 0.6))

        self.cursor_y += box_height + 16.0

    def add_paragraph(self, text: str, font_size: float = 8.5):
        if self.cursor_y + 25.0 > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
            self._new_page()

        # Word wrap text cleanly across content width
        words = text.split()
        lines = []
        current_line = []
        max_chars_per_line = int(self.CONTENT_WIDTH / (font_size * 0.48))

        for word in words:
            if len(" ".join(current_line + [word])) <= max_chars_per_line:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        for line in lines:
            if self.cursor_y + 12.0 > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
                self._new_page()
            self.current_page.insert_text((self.MARGIN_LEFT, self.cursor_y + 10.0), line, fontsize=font_size, fontname="helv", color=(0.2, 0.25, 0.35))
            self.cursor_y += font_size + 3.5
        self.cursor_y += 6.0

    def add_table(self, headers: List[str], rows: List[List[str]], col_ratios: Optional[List[float]] = None):
        """Draws a professional, paginated table with header styling and zebra rows."""
        num_cols = len(headers)
        if col_ratios and len(col_ratios) == num_cols:
            tot = sum(col_ratios)
            col_widths = [(r / tot) * self.CONTENT_WIDTH for r in col_ratios]
        else:
            col_widths = [self.CONTENT_WIDTH / num_cols] * num_cols

        row_height = 18.0

        def draw_table_header():
            header_rect = pymupdf.Rect(self.MARGIN_LEFT, self.cursor_y, self.PAGE_WIDTH - self.MARGIN_RIGHT, self.cursor_y + row_height)
            self.current_page.draw_rect(header_rect, color=(0.1, 0.15, 0.25), fill=(0.1, 0.15, 0.25))

            cur_x = self.MARGIN_LEFT
            for idx, h_text in enumerate(headers):
                w = col_widths[idx]
                self.current_page.insert_text(
                    (cur_x + 6.0, self.cursor_y + 12.5),
                    str(h_text).upper()[:24],
                    fontsize=7.5,
                    fontname="hebo",
                    color=(1.0, 1.0, 1.0),
                )
                cur_x += w
            self.cursor_y += row_height

        # Initial table header
        if self.cursor_y + row_height * 3 > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
            self._new_page()
        draw_table_header()

        # Rows
        for r_idx, row in enumerate(rows):
            if self.cursor_y + row_height > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
                self._new_page()
                draw_table_header()

            fill_color = (0.97, 0.98, 1.0) if (r_idx % 2 == 1) else (1.0, 1.0, 1.0)
            row_rect = pymupdf.Rect(self.MARGIN_LEFT, self.cursor_y, self.PAGE_WIDTH - self.MARGIN_RIGHT, self.cursor_y + row_height)
            self.current_page.draw_rect(row_rect, color=(0.88, 0.9, 0.94), fill=fill_color, width=0.5)

            cur_x = self.MARGIN_LEFT
            for c_idx, val in enumerate(row):
                if c_idx >= num_cols:
                    break
                w = col_widths[c_idx]
                str_val = str(val if val is not None else "—")
                # Truncate text that would overflow column
                max_chars = max(3, int(w / 5.2))
                display_val = (str_val[: max_chars - 2] + "..") if len(str_val) > max_chars else str_val
                
                font = "hebo" if c_idx == 0 else "helv"
                color = (0.1, 0.15, 0.25) if c_idx == 0 else (0.25, 0.3, 0.4)

                self.current_page.insert_text(
                    (cur_x + 6.0, self.cursor_y + 12.0),
                    display_val,
                    fontsize=8.0,
                    fontname=font,
                    color=color,
                )
                cur_x += w

            self.cursor_y += row_height

        self.cursor_y += 14.0

    def add_methodology_box(self, methodology_text: str, assumptions: List[str]):
        if self.cursor_y + 70.0 > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
            self._new_page()

        box_top = self.cursor_y
        self.add_section_heading("Audit Traceability & Methodology")
        self.add_paragraph(methodology_text, font_size=8.0)

        if assumptions:
            for a in assumptions[:3]:
                if self.cursor_y + 14.0 > self.PAGE_HEIGHT - self.MARGIN_BOTTOM:
                    self._new_page()
                bullet_str = f"• {a}"
                self.current_page.insert_text((self.MARGIN_LEFT + 8.0, self.cursor_y + 9.0), bullet_str[:110], fontsize=7.5, fontname="helv", color=(0.4, 0.45, 0.55))
                self.cursor_y += 12.0

        self.cursor_y += 10.0

    def finalize(self) -> bytes:
        total_pages = len(self.doc)
        for p_idx, page in enumerate(self.doc):
            p_num = p_idx + 1
            footer_line_y = self.PAGE_HEIGHT - self.MARGIN_BOTTOM + 12.0
            page.draw_line(
                pymupdf.Point(self.MARGIN_LEFT, footer_line_y),
                pymupdf.Point(self.PAGE_WIDTH - self.MARGIN_RIGHT, footer_line_y),
                color=(0.85, 0.88, 0.92),
                width=0.75,
            )

            left_footer = "PRAGYA Platform — National Statistical Cadre Competency Intelligence | Ministry of Statistics and Programme Implementation"
            right_footer = f"Page {p_num} of {total_pages}"

            page.insert_text((self.MARGIN_LEFT, footer_line_y + 11.0), left_footer, fontsize=7.0, fontname="helv", color=(0.5, 0.55, 0.65))
            page.insert_text((self.PAGE_WIDTH - self.MARGIN_RIGHT - 55.0, footer_line_y + 11.0), right_footer, fontsize=7.5, fontname="hebo", color=(0.3, 0.35, 0.45))

        return self.doc.tobytes()
