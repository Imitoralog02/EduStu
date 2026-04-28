from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QFrame, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from views.base_view import BaseView, QSS_INPUT
from controllers.course import CourseController
from utils.config import TEXT_MUTED, TEXT_LIGHT

COLS = ["Mã HP", "Tên học phần", "Tín chỉ", "Giảng viên", "Học kỳ"]

# Mapping prefix mã HP → tên khoa
_PREFIX_TO_KHOA = {
    "CNTT":  "Công nghệ thông tin",
    "KT":    "Kinh tế",
    "XD":    "Xây dựng",
    "DL":    "Du lịch",
    "CK":    "Cơ khí",
    "DTE":   "Điện tử",
    "DUOC":  "Dược",
    "DDU":   "Điều dưỡng",
    "LUAT":  "Luật",
    "KTOAN": "Kế toán",
    "NNGU":  "Ngôn ngữ",
}

def _get_khoa(ma_hp: str) -> str:
    ma = (ma_hp or "").upper()
    # Khớp prefix dài trước (tránh "KT" khớp nhầm "KTOAN")
    for prefix in sorted(_PREFIX_TO_KHOA.keys(), key=len, reverse=True):
        if ma.startswith(prefix):
            return _PREFIX_TO_KHOA[prefix]
    return "Khác"


class KhoaButton(QPushButton):
    def __init__(self, label: str, count: int):
        super().__init__()
        self._label = label
        self.setCheckable(True)
        self.setFixedHeight(52)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._count = count
        self._update_text()
        self._apply_style(False)

    def _update_text(self):
        self.setText(f"  {self._label}\n  {self._count} học phần")

    def update_count(self, count: int):
        self._count = count
        self._update_text()

    def _apply_style(self, checked: bool):
        if checked:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(37,99,235,0.18);
                    color: #BFDBFE;
                    border: none;
                    border-left: 4px solid #2563EB;
                    border-radius: 0px;
                    text-align: left;
                    font-size: 13px;
                    font-family: Arial;
                    font-weight: 700;
                    padding-left: 8px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_MUTED};
                    border: none;
                    border-left: 4px solid transparent;
                    border-radius: 0px;
                    text-align: left;
                    font-size: 13px;
                    font-family: Arial;
                    padding-left: 8px;
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.06);
                    color: {TEXT_LIGHT};
                    border-left: 4px solid rgba(37,99,235,0.5);
                }}
            """)

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self._apply_style(checked)


class CourseView(BaseView):
    PAGE_TITLE = "Học phần"
    PAGE_SUB   = "Danh mục học phần (chỉ xem)"

    def __init__(self):
        self._ctrl = CourseController()
        self._all_courses: list = []
        self._selected_khoa: str = "Tất cả"
        super().__init__()

    def build_ui(self):

        main = QHBoxLayout()
        main.setSpacing(14)

        # ── Sidebar khoa ──────────────────────────────────────────────────
        self._sidebar = QFrame()
        self._sidebar.setFixedWidth(200)
        self._sidebar.setStyleSheet(f"""
            QFrame {{
                background: rgba(10,22,40,0.6);
                border-radius: 14px;
                border: 1px solid rgba(255,255,255,0.08);
            }}
        """)
        sh = QGraphicsDropShadowEffect(self._sidebar)
        sh.setBlurRadius(20); sh.setOffset(0, 3)
        sh.setColor(QColor(0, 0, 0, 60))
        self._sidebar.setGraphicsEffect(sh)

        sb_lay = QVBoxLayout(self._sidebar)
        sb_lay.setContentsMargins(0, 12, 0, 12)
        sb_lay.setSpacing(2)

        title_lbl = QLabel("  Khoa / Bộ môn")
        title_lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-weight:700;"
                                 "font-family:Arial;border:none;letter-spacing:1px;padding-left:8px;")
        sb_lay.addWidget(title_lbl)
        sb_lay.addSpacing(6)

        self._khoa_btns: dict[str, KhoaButton] = {}
        self._sb_layout = sb_lay
        sb_lay.addStretch()
        main.addWidget(self._sidebar)

        # ── Phần phải: search + table ─────────────────────────────────────
        right = QVBoxLayout()
        right.setSpacing(10)

        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm mã HP hoặc tên học phần...")
        self.inp_search.setFixedHeight(34)
        self.inp_search.setStyleSheet(QSS_INPUT)
        self.inp_search.textChanged.connect(self._filter)
        right.addWidget(self.inp_search)

        self._info_lbl = QLabel("")
        self._info_lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:13px;font-family:Arial;")
        right.addWidget(self._info_lbl)

        self.table = self.make_table(COLS)
        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(1, 240)
        self.table.setColumnWidth(2, 70)
        self.table.setColumnWidth(3, 170)
        self.table.setColumnWidth(4, 130)
        right.addWidget(self.table)
        main.addLayout(right, stretch=1)

        self._root.addLayout(main)

    def refresh(self):
        self._reload()

    def _reload(self):
        from models.course import Course as _Course
        self.run_async(
            lambda: [_Course.from_dict(c) for c in self._ctrl._svc.get_list(search="")],
            self._on_loaded,
        )

    def _on_loaded(self, courses):
        self._all_courses = courses
        self._rebuild_sidebar(courses)
        self._filter()

    def _rebuild_sidebar(self, courses):
        # Tính số lượng theo khoa
        khoa_count: dict[str, int] = {}
        for c in courses:
            k = _get_khoa(c.ma_hp)
            khoa_count[k] = khoa_count.get(k, 0) + 1

        all_count = len(courses)
        all_khoas = ["Tất cả"] + sorted(khoa_count.keys())

        # Xóa buttons cũ (giữ title + stretch)
        for btn in self._khoa_btns.values():
            btn.deleteLater()
        self._khoa_btns.clear()

        # Xóa layout cũ trừ title (index 0) và stretch (cuối)
        while self._sb_layout.count() > 2:
            item = self._sb_layout.takeAt(1)
            if item and item.widget():
                item.widget().deleteLater()

        # Thêm buttons
        for khoa in all_khoas:
            count = all_count if khoa == "Tất cả" else khoa_count.get(khoa, 0)
            btn = KhoaButton(khoa, count)
            btn.setChecked(khoa == self._selected_khoa)
            btn.clicked.connect(lambda _, k=khoa: self._select_khoa(k))
            self._khoa_btns[khoa] = btn
            # Insert trước stretch (last item)
            self._sb_layout.insertWidget(self._sb_layout.count() - 1, btn)

    def _select_khoa(self, khoa: str):
        self._selected_khoa = khoa
        for k, btn in self._khoa_btns.items():
            btn.setChecked(k == khoa)
        self._filter()

    def _filter(self):
        search = self.inp_search.text().strip().lower() if hasattr(self, "inp_search") else ""
        filtered = [
            c for c in self._all_courses
            if (self._selected_khoa == "Tất cả" or _get_khoa(c.ma_hp) == self._selected_khoa)
            and (not search or search in c.ma_hp.lower() or search in (c.ten_hp or "").lower())
        ]
        self._render(filtered)

    def _render(self, courses):
        khoa_label = "" if self._selected_khoa == "Tất cả" else f" — {self._selected_khoa}"
        self._info_lbl.setText(f"{len(courses)} học phần{khoa_label}")
        self.table.setRowCount(len(courses))
        for row, c in enumerate(courses):
            self.table.setItem(row, 0, self.cell(c.ma_hp))
            self.table.setItem(row, 1, self.cell(c.ten_hp, bold=True))
            self.table.setItem(row, 2, self.cell(str(c.so_tin_chi), align=Qt.AlignmentFlag.AlignCenter))
            self.table.setItem(row, 3, self.cell(c.giao_vien or "—"))
            self.table.setItem(row, 4, self.cell(c.hoc_ky or "—"))
