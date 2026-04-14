from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QLineEdit, QWidget, QPushButton,
    QDialog, QGridLayout, QLabel, QSpinBox, QComboBox, QFrame, QMessageBox, QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from views.base_view import BaseView, QSS_INPUT
from controllers.course import CourseController
from utils.config import PRIMARY, SECONDARY, BORDER, TEXT_LIGHT, TEXT_MUTED, ACCENT, HIGHLIGHT, DANGER, HOC_KY_LIST

COLS = ["Mã HP", "Tên học phần", "Tín chỉ", "Giảng viên", "Học kỳ", "Thao tác"]


class CourseView(BaseView):
    PAGE_TITLE = "Học phần"
    PAGE_SUB   = "Danh mục học phần"

    def __init__(self):
        self._ctrl = CourseController()
        super().__init__()

    def build_ui(self):
        btn_add = self.make_btn("+ Thêm HP", "primary")
        btn_add.clicked.connect(lambda: CourseForm(on_save=self.refresh).exec())
        self.add_action(btn_add)

        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm mã HP hoặc tên...")
        self.inp_search.setFixedHeight(34)
        self.inp_search.setStyleSheet(QSS_INPUT)
        self.inp_search.textChanged.connect(self.refresh)
        self._root.addWidget(self.inp_search)

        self.table = self.make_table(COLS)
        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(2, 70)
        self.table.setColumnWidth(3, 170)
        self.table.setColumnWidth(4, 130)
        self._root.addWidget(self.table)

    def refresh(self):
        search = self.inp_search.text().strip() if hasattr(self, "inp_search") else ""
        self._ctrl.load_list(search, on_success=self._render, on_error=self._default_error)

    def _render(self, courses):
        self.set_subtitle(f"{len(courses)} học phần")
        self.table.setRowCount(len(courses))
        for row, c in enumerate(courses):
            self.table.setItem(row, 0, self.cell(c.ma_hp))
            self.table.setItem(row, 1, self.cell(c.ten_hp, bold=True))
            self.table.setItem(row, 2, self.cell(str(c.so_tin_chi), align=Qt.AlignmentFlag.AlignCenter))
            self.table.setItem(row, 3, self.cell(c.giao_vien))
            self.table.setItem(row, 4, self.cell(c.hoc_ky))
            w = QWidget()
            hl = QHBoxLayout(w)
            hl.setContentsMargins(4, 2, 4, 2)
            hl.setSpacing(4)
            for txt, fn, clr in [
                ("Sửa", lambda _, obj=c: CourseForm(data=obj.__dict__, on_save=self.refresh).exec(), ACCENT),
                ("Xóa", lambda _, m=c.ma_hp: self._delete(m), DANGER),
            ]:
                b = QPushButton(txt)
                b.setFixedHeight(26)
                b.setCursor(Qt.CursorShape.PointingHandCursor)
                b.setStyleSheet(f"QPushButton{{background:transparent;color:{clr};border:1px solid {clr};border-radius:4px;font-size:11px;padding:0 8px;}}QPushButton:hover{{background:{clr};color:white;}}")
                b.clicked.connect(fn)
                hl.addWidget(b)
            self.table.setCellWidget(row, 5, w)

    def _delete(self, ma_hp: str):
        if QMessageBox.question(self, "Xóa", f"Xóa học phần {ma_hp}?",
           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self._ctrl.delete(ma_hp, on_success=lambda _: self.refresh(), on_error=self._default_error)


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
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        root.addWidget(title)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet(f"color:{BORDER};")
        root.addWidget(sep)

        grid = QGridLayout(); grid.setSpacing(10)

        def lbl(t):
            l = QLabel(t); l.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-weight:600;"); l.setFixedWidth(110); return l

        def inp(ph=""):
            i = QLineEdit(); i.setPlaceholderText(ph); i.setFixedHeight(34); i.setStyleSheet(QSS_INPUT); return i

        self.f_ma   = inp("VD: CS101")
        self.f_ten  = inp("Tên học phần")
        self.f_tc   = QSpinBox(); self.f_tc.setRange(1,10); self.f_tc.setValue(3); self.f_tc.setFixedHeight(34); self.f_tc.setStyleSheet(QSS_INPUT)
        self.f_gv   = inp("Tên giảng viên")
        self.f_hk   = QComboBox(); self.f_hk.addItems(HOC_KY_LIST); self.f_hk.setFixedHeight(34); self.f_hk.setStyleSheet(QSS_INPUT)

        for i,(l,w) in enumerate([("Mã HP *",self.f_ma),("Tên HP *",self.f_ten),("Tín chỉ",self.f_tc),("Giảng viên",self.f_gv),("Học kỳ",self.f_hk)]):
            grid.addWidget(lbl(l),i,0); grid.addWidget(w,i,1)
        root.addLayout(grid); root.addStretch()

        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Hủy"); bc.setFixedHeight(34); bc.clicked.connect(self.reject)
        bc.setStyleSheet(f"QPushButton{{background:transparent;color:{TEXT_MUTED};border:1px solid {BORDER};border-radius:6px;padding:0 16px;}}QPushButton:hover{{color:{TEXT_LIGHT};}}")
        self.bs = QPushButton("Lưu"); self.bs.setFixedHeight(34); self.bs.clicked.connect(self._save)
        self.bs.setStyleSheet(f"QPushButton{{background:{HIGHLIGHT};color:white;border:none;border-radius:6px;font-weight:700;padding:0 20px;}}QPushButton:hover{{background:#c73050;}}")
        btn_row.addWidget(bc); btn_row.addWidget(self.bs); root.addLayout(btn_row)

    def _fill(self, d):
        self.f_ma.setText(d.get("ma_hp","")); self.f_ma.setReadOnly(True)
        self.f_ten.setText(d.get("ten_hp",""))
        self.f_tc.setValue(d.get("so_tin_chi",3))
        self.f_gv.setText(d.get("giao_vien",""))
        idx = self.f_hk.findText(d.get("hoc_ky",""))
        if idx >= 0: self.f_hk.setCurrentIndex(idx)

    def _save(self):
        data = {"ma_hp": self.f_ma.text().strip(), "ten_hp": self.f_ten.text().strip(),
                "so_tin_chi": self.f_tc.value(), "giao_vien": self.f_gv.text().strip(),
                "hoc_ky": self.f_hk.currentText()}
        self.bs.setEnabled(False)
        def ok(_):
            if self._on_save: self._on_save()
            self.accept()
        def err(msg):
            self.bs.setEnabled(True)
            QMessageBox.warning(self, "Lỗi", msg)
        if self._is_edit:
            self._ctrl.update(data["ma_hp"], data, on_success=ok, on_error=err)
        else:
            self._ctrl.create(data, on_success=ok, on_error=err)