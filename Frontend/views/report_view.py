from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLabel, QFrame,
    QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from views.base_view import BaseView
from controllers.report import ReportController
from utils.config import (PRIMARY, SECONDARY, BORDER, TEXT_LIGHT, TEXT_MUTED,
                           ACCENT, HIGHLIGHT, SUCCESS, WARNING, DANGER)

COLS_TK = ["Khoa", "Tổng SV", "Đang học", "GPA TB", "Tỉ lệ đạt", "Cảnh báo HV"]
EXPORTS = [
    ("Danh sách sinh viên",  "sinhvien",  "Xuất toàn bộ SV ra .xlsx",      ACCENT),
    ("Bảng điểm tổng hợp",   "bangdiem",  "Xuất điểm tất cả học phần",      SUCCESS),
    ("Danh sách công nợ",    "conno",     "SV còn nợ học phí kỳ này",        DANGER),
]


class ReportView(BaseView):
    PAGE_TITLE = "Báo cáo & Thống kê"
    PAGE_SUB   = "Xuất file và thống kê theo khoa"

    def __init__(self):
        self._ctrl = ReportController()
        super().__init__()

    def build_ui(self):
        # Export cards
        exp_lbl = QLabel("Xuất file báo cáo")
        exp_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        exp_lbl.setStyleSheet(f"color: {TEXT_LIGHT};")
        self._root.addWidget(exp_lbl)

        exp_row = QHBoxLayout(); exp_row.setSpacing(12)
        for title, loai, desc, clr in EXPORTS:
            exp_row.addWidget(self._export_card(title, desc, loai, clr))
        self._root.addLayout(exp_row)

        # Statistics table
        stat_lbl = QLabel("Thống kê theo khoa")
        stat_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        stat_lbl.setStyleSheet(f"color: {TEXT_LIGHT};")
        self._root.addWidget(stat_lbl)

        self.table = self.make_table(COLS_TK)
        self.table.setMaximumHeight(260)
        self._root.addWidget(self.table)
        self._root.addStretch()

    def refresh(self):
        self._ctrl.load_statistics(on_success=self._render_stats, on_error=lambda _: None)

    def _render_stats(self, items: list):
        self.table.setRowCount(len(items))
        for row, k in enumerate(items):
            self.table.setItem(row, 0, self.cell(k.get("khoa", ""), bold=True))
            self.table.setItem(row, 1, self.cell(str(k.get("tong_sv", 0))))
            self.table.setItem(row, 2, self.cell(str(k.get("dang_hoc", 0))))
            gpa = k.get("gpa_tb")
            self.table.setItem(row, 3, self.cell(f"{gpa:.2f}" if gpa else "—"))
            tl = k.get("ti_le_dat")
            self.table.setItem(row, 4, self.cell(f"{tl:.1f}%" if tl else "—"))
            self.table.setItem(row, 5, self.cell(str(k.get("canh_bao_hv", 0))))

    def _export_card(self, title: str, desc: str, loai: str, clr: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {SECONDARY};
                border: 1px solid {BORDER};
                border-top: 3px solid {clr};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_t.setStyleSheet(f"color: {TEXT_LIGHT}; border: none;")

        lbl_d = QLabel(desc)
        lbl_d.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; border: none;")

        btn = QPushButton("Xuất Excel")
        btn.setFixedHeight(32)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {clr};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{ opacity: 0.85; }}
        """)
        btn.clicked.connect(lambda: self._do_export(loai))

        layout.addWidget(lbl_t)
        layout.addWidget(lbl_d)
        layout.addStretch()
        layout.addWidget(btn)
        return card

    def _do_export(self, loai: str):
        names = {
            "sinhvien": "danh_sach_sv.xlsx",
            "bangdiem": "bang_diem.xlsx",
            "conno":    "cong_no.xlsx",
        }
        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu file Excel", names.get(loai, "export.xlsx"), "Excel (*.xlsx)"
        )
        if not path:
            return
        self._ctrl.export_excel(
            loai, path,
            on_success=lambda p: QMessageBox.information(self, "Thành công", f"Đã xuất file:\n{p}"),
            on_error=self._default_error,
        )