from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLabel, QFrame,
    QPushButton, QFileDialog, QMessageBox,
    QGraphicsDropShadowEffect, QSizePolicy, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView,
)
from PyQt6.QtCore import Qt, QRectF, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush
from views.base_view import BaseView
from controllers.report import ReportController
from utils.config import (
    TEXT_LIGHT, TEXT_MUTED, ACCENT, SUCCESS, WARNING, DANGER, INFO, BORDER,
)

COLS_TK = ["Khoa", "Tổng SV", "Đang học", "GPA TB", "Tỉ lệ đạt", "Cảnh báo HV"]

EXPORTS = [
    ("📋  Danh sách sinh viên", "sinhvien", "Xuất toàn bộ hồ sơ sinh viên",       ACCENT,   "danh_sach_sv.xlsx"),
    ("📊  Bảng điểm tổng hợp",  "bangdiem", "Điểm tất cả môn học của tất cả SV",  SUCCESS,  "bang_diem.xlsx"),
    ("💸  Danh sách công nợ",   "conno",    "Sinh viên còn nợ học phí",            DANGER,   "cong_no.xlsx"),
]


# ── Mini bar chart dùng QPainter ─────────────────────────────────────────────

class MiniBarChart(QFrame):
    """Bar chart ngang đơn giản cho 1 chỉ số theo khoa."""

    def __init__(self, bar_color: str = ACCENT, unit: str = ""):
        super().__init__()
        self._data: list[tuple[str, float]] = []
        self._color = bar_color
        self._unit = unit
        self._max_val = 1.0
        self.setStyleSheet("background:transparent;border:none;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, data: list[tuple[str, float]]):
        self._data = sorted(data, key=lambda x: x[1], reverse=True)
        self._max_val = max((v for _, v in data), default=1) or 1
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        label_w = 155
        value_w = 50
        bar_area = w - label_w - value_w - 8
        n = len(self._data)
        if n == 0 or bar_area <= 0:
            p.end(); return

        row_h = (h - 8) / n

        for i, (label, value) in enumerate(self._data):
            y = 4 + i * row_h
            bar_h = max(row_h * 0.52, 12)
            bar_y = y + (row_h - bar_h) / 2
            bar_w = bar_area * value / self._max_val

            # Nền
            p.setBrush(QBrush(QColor("#F1F5F9")))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(QRectF(label_w, bar_y, bar_area, bar_h), 4, 4)

            # Bar
            p.setBrush(QBrush(QColor(self._color)))
            if bar_w > 0:
                p.drawRoundedRect(QRectF(label_w, bar_y, bar_w, bar_h), 4, 4)

            # Label
            short = label if len(label) <= 24 else label[:22] + "…"
            p.setPen(QPen(QColor("#475569")))
            p.setFont(QFont("Arial", 10))
            p.drawText(QRect(0, int(bar_y), label_w - 6, int(bar_h)),
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, short)

            # Giá trị
            val_str = f"{value:.2f}{self._unit}" if isinstance(value, float) else f"{value}{self._unit}"
            p.setPen(QPen(QColor(self._color)))
            p.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            p.drawText(QRect(int(label_w + bar_w + 6), int(bar_y), value_w, int(bar_h)),
                       Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, val_str)

        p.end()


# ── ReportView ───────────────────────────────────────────────────────────────

class ReportView(BaseView):
    PAGE_TITLE = "Báo cáo & Thống kê"
    PAGE_SUB   = "Tổng hợp số liệu toàn trường và xuất file"

    def __init__(self):
        self._ctrl = ReportController()
        super().__init__()

    # ── Build UI ──────────────────────────────────────────────────────────

    def build_ui(self):
        # ── Row 1: KPI tổng hợp toàn trường ─────────────────────────────
        kpi_row = QHBoxLayout(); kpi_row.setSpacing(12)
        kpi_defs = [
            ("tong_sv",    "Tổng sinh viên",    "—", ACCENT,   "👥"),
            ("gpa_tb",     "GPA TB toàn trường","—", SUCCESS,  "🎓"),
            ("ti_le_dat",  "Tỉ lệ đạt",         "—", INFO,     "✅"),
            ("canh_bao",   "Cảnh báo học vụ",   "—", WARNING,  "⚠️"),
        ]
        self._kpi: dict[str, QLabel] = {}
        for key, label, val, clr, icon in kpi_defs:
            card, lbl_val = self._kpi_card(label, val, clr, icon)
            self._kpi[key] = lbl_val
            kpi_row.addWidget(card)
        self._root.addLayout(kpi_row)

        # ── Row 2: Bảng thống kê chi tiết theo khoa ─────────────────────
        tbl_lbl = QLabel("Thống kê chi tiết theo khoa")
        tbl_lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        tbl_lbl.setStyleSheet(f"color:{TEXT_LIGHT};font-family:Arial;background:transparent;")
        self._root.addWidget(tbl_lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(len(COLS_TK))
        self.table.setHorizontalHeaderLabels(COLS_TK)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setStyleSheet(
            f"background:#F1F5F9;color:#475569;font-size:12px;font-weight:700;border:none;"
        )
        self.table.setStyleSheet("""
            QTableWidget {
                background: #FFFFFF; border: 1px solid #E2E8F0;
                border-radius: 10px; gridline-color: #F1F5F9;
                font-family: Arial; font-size: 13px;
            }
            QTableWidget::item { padding: 8px 12px; color: #1E293B; border: none; }
            QTableWidget::item:selected { background: #DBEAFE; color: #1E293B; }
            QTableWidget::item:alternate { background: #F8FAFC; }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.setMaximumHeight(240)
        self.table.verticalHeader().setDefaultSectionSize(38)
        self._root.addWidget(self.table)

        # ── Row 3: Biểu đồ GPA và Tỉ lệ đạt theo khoa ──────────────────
        chart_row = QHBoxLayout(); chart_row.setSpacing(12)

        gpa_card = self._chart_card("GPA trung bình theo khoa")
        self._chart_gpa = MiniBarChart(bar_color=SUCCESS, unit="")
        gpa_card.layout().addWidget(self._chart_gpa)

        tl_card = self._chart_card("Tỉ lệ đạt theo khoa (%)")
        self._chart_tl = MiniBarChart(bar_color=INFO, unit="%")
        tl_card.layout().addWidget(self._chart_tl)

        chart_row.addWidget(gpa_card)
        chart_row.addWidget(tl_card)
        self._root.addLayout(chart_row)

        # ── Row 4: Xuất file ─────────────────────────────────────────────
        exp_lbl = QLabel("Xuất file báo cáo")
        exp_lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        exp_lbl.setStyleSheet(f"color:{TEXT_LIGHT};font-family:Arial;background:transparent;")
        self._root.addWidget(exp_lbl)

        exp_row = QHBoxLayout(); exp_row.setSpacing(12)
        for title, loai, desc, clr, fname in EXPORTS:
            exp_row.addWidget(self._export_card(title, desc, loai, clr, fname))
        self._root.addLayout(exp_row)

    # ── Refresh ───────────────────────────────────────────────────────────

    def refresh(self):
        self._ctrl.load_statistics(on_success=self._render_stats, on_error=lambda _: None)

    # ── Render ────────────────────────────────────────────────────────────

    def _render_stats(self, items: list):
        # KPI tổng hợp từ dữ liệu các khoa
        tong_sv   = sum(k.get("tong_sv", 0) for k in items)
        cb_total  = sum(k.get("canh_bao_hv", 0) for k in items)

        # GPA TB toàn trường (weighted average theo tổng SV)
        gpa_vals = [(k.get("gpa_tb") or 0) * k.get("tong_sv", 0) for k in items]
        sv_with_gpa = sum(k.get("tong_sv", 0) for k in items if k.get("gpa_tb"))
        gpa_tb = sum(gpa_vals) / sv_with_gpa if sv_with_gpa > 0 else None

        # Tỉ lệ đạt TB toàn trường
        tl_vals = [(k.get("ti_le_dat") or 0) * k.get("tong_sv", 0) for k in items]
        sv_with_tl = sum(k.get("tong_sv", 0) for k in items if k.get("ti_le_dat"))
        tl_tb = sum(tl_vals) / sv_with_tl if sv_with_tl > 0 else None

        self._kpi["tong_sv"].setText(str(tong_sv))
        self._kpi["gpa_tb"].setText(f"{gpa_tb:.2f}" if gpa_tb else "—")
        self._kpi["ti_le_dat"].setText(f"{tl_tb:.1f}%" if tl_tb else "—")
        self._kpi["canh_bao"].setText(str(cb_total))

        # Bảng chi tiết
        self.table.setRowCount(len(items))
        sorted_items = sorted(items, key=lambda x: x.get("tong_sv", 0), reverse=True)
        for row, k in enumerate(sorted_items):
            gpa  = k.get("gpa_tb")
            tl   = k.get("ti_le_dat")
            canh = k.get("canh_bao_hv", 0)

            self._set_cell(row, 0, k.get("khoa", ""), bold=True)
            self._set_cell(row, 1, str(k.get("tong_sv", 0)), center=True)
            self._set_cell(row, 2, str(k.get("dang_hoc", 0)), center=True)

            gpa_str = f"{gpa:.2f}" if gpa else "—"
            gpa_clr = (SUCCESS if gpa and gpa >= 7.0 else
                       WARNING if gpa and gpa >= 5.0 else
                       DANGER  if gpa else None)
            self._set_cell(row, 3, gpa_str, center=True, color=gpa_clr)

            tl_str = f"{tl:.1f}%" if tl else "—"
            tl_clr = (SUCCESS if tl and tl >= 80 else
                      WARNING if tl and tl >= 60 else
                      DANGER  if tl else None)
            self._set_cell(row, 4, tl_str, center=True, color=tl_clr)

            cb_clr = DANGER if canh > 0 else None
            self._set_cell(row, 5, str(canh), center=True, color=cb_clr)

        # Biểu đồ
        self._chart_gpa.set_data([
            (k.get("khoa", ""), k.get("gpa_tb") or 0) for k in items
        ])
        self._chart_tl.set_data([
            (k.get("khoa", ""), k.get("ti_le_dat") or 0) for k in items
        ])

    # ── Helpers ───────────────────────────────────────────────────────────

    def _kpi_card(self, label: str, val: str, clr: str, icon: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: #FFFFFF; border: none;
                border-top: 4px solid {clr}; border-radius: 14px;
            }}
        """)
        sh = QGraphicsDropShadowEffect(card)
        sh.setBlurRadius(18); sh.setOffset(0, 3); sh.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(sh)

        lay = QHBoxLayout(card); lay.setContentsMargins(16, 14, 16, 14); lay.setSpacing(12)

        ic = QLabel(icon)
        ic.setFixedSize(42, 42)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet(f"background:{clr}22;border-radius:21px;font-size:18px;border:none;")
        lay.addWidget(ic)

        col = QVBoxLayout(); col.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet("color:#64748B;font-size:12px;font-family:Arial;border:none;font-weight:600;")
        lbl_val = QLabel(val)
        lbl_val.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        lbl_val.setStyleSheet(f"color:{clr};border:none;")
        col.addWidget(lbl); col.addWidget(lbl_val)
        lay.addLayout(col); lay.addStretch()
        return card, lbl_val

    def _chart_card(self, title: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #FFFFFF; border: 1px solid #E2E8F0;
                border-radius: 14px;
            }
        """)
        sh = QGraphicsDropShadowEffect(card)
        sh.setBlurRadius(16); sh.setOffset(0, 3); sh.setColor(QColor(0, 0, 0, 25))
        card.setGraphicsEffect(sh)
        card.setMinimumHeight(200)

        lay = QVBoxLayout(card); lay.setContentsMargins(18, 14, 18, 14); lay.setSpacing(8)
        t = QLabel(title)
        t.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        t.setStyleSheet("color:#0F172A;border:none;")
        lay.addWidget(t)
        return card

    def _set_cell(self, row: int, col: int, text: str,
                  bold: bool = False, center: bool = False, color: str = None):
        item = QTableWidgetItem(text)
        if bold:
            item.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        else:
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        if color:
            item.setForeground(QColor(color))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, col, item)

    def _export_card(self, title: str, desc: str, loai: str, clr: str, fname: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: #FFFFFF; border: none;
                border-left: 5px solid {clr}; border-radius: 14px;
            }}
        """)
        sh = QGraphicsDropShadowEffect(card)
        sh.setBlurRadius(14); sh.setOffset(0, 3); sh.setColor(QColor(0, 0, 0, 22))
        card.setGraphicsEffect(sh)

        lay = QVBoxLayout(card); lay.setContentsMargins(18, 14, 18, 14); lay.setSpacing(6)

        t = QLabel(title)
        t.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        t.setStyleSheet("color:#0F172A;border:none;")

        d = QLabel(desc)
        d.setStyleSheet("color:#64748B;font-size:12px;font-family:Arial;border:none;")
        d.setWordWrap(True)

        btn = QPushButton("⬇  Xuất Excel")
        btn.setFixedHeight(34)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {clr}; color: white; border: none;
                border-radius: 8px; font-size: 12px; font-weight: 700;
                font-family: Arial;
            }}
            QPushButton:hover {{ background: {clr}CC; }}
        """)
        btn.clicked.connect(lambda checked=False, l=loai, f=fname: self._do_export(l, f))

        lay.addWidget(t); lay.addWidget(d); lay.addStretch(); lay.addWidget(btn)
        return card

    def _do_export(self, loai: str, fname: str):
        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu file Excel", fname, "Excel (*.xlsx)"
        )
        if not path:
            return
        self._ctrl.export_excel(
            loai, path,
            on_success=lambda p: QMessageBox.information(self, "Thành công", f"Đã xuất:\n{p}"),
            on_error=self._default_error,
        )
