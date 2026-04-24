from __future__ import annotations
import re
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLineEdit, QWidget, QPushButton,
    QDialog, QGridLayout, QLabel, QSpinBox, QComboBox, QFrame,
    QMessageBox, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from views.base_view import BaseView, QSS_INPUT
from controllers.course import CourseController
from utils.config import (
    PRIMARY, BORDER, TEXT_LIGHT, TEXT_MUTED, ACCENT, DANGER, HOC_KY_LIST, INFO,
)

COLS = ["Mã HP", "Tên học phần", "Tín chỉ", "Giảng viên", "Học kỳ", "Thao tác"]

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
    PAGE_SUB   = "Danh mục học phần theo khoa"

    def __init__(self):
        self._ctrl = CourseController()
        self._all_courses: list = []
        self._selected_khoa: str = "Tất cả"
        super().__init__()

    def build_ui(self):
        btn_add = self.make_btn("+ Thêm HP", "primary")
        btn_add.clicked.connect(lambda: CourseForm(on_save=self._reload).exec())
        self.add_action(btn_add)

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

            w = QWidget()
            hl = QHBoxLayout(w)
            hl.setContentsMargins(4, 2, 4, 2)
            hl.setSpacing(4)
            for txt, fn, clr in [
                ("Sửa", lambda _, obj=c: CourseForm(data=obj.__dict__, on_save=self._reload).exec(), ACCENT),
                ("Xóa", lambda _, m=c.ma_hp: self._delete(m), DANGER),
            ]:
                b = QPushButton(txt)
                b.setFixedHeight(26)
                b.setCursor(Qt.CursorShape.PointingHandCursor)
                b.setStyleSheet(
                    f"QPushButton{{background:transparent;color:{clr};border:1px solid {clr};"
                    f"border-radius:4px;font-size:11px;padding:0 8px;}}"
                    f"QPushButton:hover{{background:{clr};color:white;}}"
                )
                b.clicked.connect(fn)
                hl.addWidget(b)
            self.table.setCellWidget(row, 5, w)

    def _delete(self, ma_hp: str):
        if QMessageBox.question(
            self, "Xóa", f"Xóa học phần {ma_hp}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self._ctrl.delete(ma_hp, on_success=lambda _: self._reload(), on_error=self._default_error)


class CourseForm(QDialog):
    def __init__(self, data: dict | None = None, on_save=None):
        super().__init__()
        self._data    = data or {}
        self._on_save = on_save
        self._ctrl    = CourseController()
        self._is_edit = bool(data)
        self.setWindowTitle("Sửa học phần" if self._is_edit else "Thêm học phần")
        self.setFixedSize(420, 340)
        self.setStyleSheet(f"background: {PRIMARY}; color: {TEXT_LIGHT};")
        self._build()
        if data:
            self._fill(data)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)
        title = QLabel(self.windowTitle())
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        root.addWidget(title)
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{BORDER};")
        root.addWidget(sep)

        grid = QGridLayout()
        grid.setSpacing(10)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-weight:600;")
            l.setFixedWidth(110)
            return l

        def inp(ph=""):
            i = QLineEdit()
            i.setPlaceholderText(ph)
            i.setFixedHeight(34)
            i.setStyleSheet(QSS_INPUT)
            return i

        self.f_ma  = inp("VD: CS101")
        self.f_ten = inp("Tên học phần")
        self.f_tc  = QSpinBox()
        self.f_tc.setRange(1, 10)
        self.f_tc.setValue(3)
        self.f_tc.setFixedHeight(34)
        self.f_tc.setStyleSheet(QSS_INPUT)
        self.f_gv  = inp("Tên giảng viên")
        self.f_hk  = QComboBox()
        self.f_hk.addItems(HOC_KY_LIST)
        self.f_hk.setFixedHeight(34)
        self.f_hk.setStyleSheet(QSS_INPUT)

        for i, (l, w) in enumerate([
            ("Mã HP *", self.f_ma), ("Tên HP *", self.f_ten),
            ("Tín chỉ", self.f_tc), ("Giảng viên", self.f_gv), ("Học kỳ", self.f_hk),
        ]):
            grid.addWidget(lbl(l), i, 0)
            grid.addWidget(w, i, 1)
        root.addLayout(grid)
        root.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        bc = QPushButton("Hủy")
        bc.setFixedHeight(34)
        bc.clicked.connect(self.reject)
        bc.setStyleSheet(
            f"QPushButton{{background:transparent;color:{TEXT_MUTED};border:1px solid {BORDER};"
            f"border-radius:6px;padding:0 16px;}}QPushButton:hover{{color:{TEXT_LIGHT};}}"
        )
        self.bs = QPushButton("Lưu")
        self.bs.setFixedHeight(34)
        self.bs.clicked.connect(self._save)
        self.bs.setStyleSheet(
            f"QPushButton{{background:{INFO};color:white;border:none;border-radius:6px;"
            f"font-weight:700;padding:0 20px;}}QPushButton:hover{{background:#1D4ED8;}}"
        )
        btn_row.addWidget(bc)
        btn_row.addWidget(self.bs)
        root.addLayout(btn_row)

    def _fill(self, d):
        self.f_ma.setText(d.get("ma_hp", ""))
        self.f_ma.setReadOnly(True)
        self.f_ten.setText(d.get("ten_hp", ""))
        self.f_tc.setValue(d.get("so_tin_chi", 3))
        self.f_gv.setText(d.get("giao_vien", ""))
        idx = self.f_hk.findText(d.get("hoc_ky", ""))
        if idx >= 0:
            self.f_hk.setCurrentIndex(idx)

    def _save(self):
        data = {
            "ma_hp": self.f_ma.text().strip(),
            "ten_hp": self.f_ten.text().strip(),
            "so_tin_chi": self.f_tc.value(),
            "giao_vien": self.f_gv.text().strip(),
            "hoc_ky": self.f_hk.currentText(),
        }
        self.bs.setEnabled(False)

        def ok(_):
            if self._on_save:
                self._on_save()
            self.accept()

        def err(msg):
            self.bs.setEnabled(True)
            QMessageBox.warning(self, "Lỗi", msg)

        if self._is_edit:
            self._ctrl.update(data["ma_hp"], data, on_success=ok, on_error=err)
        else:
            self._ctrl.create(data, on_success=ok, on_error=err)
