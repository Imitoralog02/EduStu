from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLineEdit, QComboBox,
    QMessageBox, QFileDialog, QWidget, QPushButton,
    QDialog, QGridLayout, QLabel, QDateEdit, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QFont
from views.base_view import BaseView, QSS_INPUT
from controllers.student import StudentController
from utils.config import (
    PRIMARY, SECONDARY, ACCENT, HIGHLIGHT, TEXT_LIGHT, TEXT_MUTED, BORDER,
    TRANG_THAI_SV, KHOA_LIST, GIOI_TINH, SUCCESS, DANGER, WARNING
)
from utils.helpers import fmt_date, badge_color

COLS = ["MSSV", "Họ và tên", "Lớp", "Khoa", "Ngày sinh", "Trạng thái", "Thao tác"]


class StudentView(BaseView):
    PAGE_TITLE = "Sinh viên"
    PAGE_SUB   = "Quản lý hồ sơ sinh viên"

    def __init__(self):
        self._ctrl = StudentController()
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._load)
        super().__init__()

    def build_ui(self):
        # Action buttons
        btn_add = self.make_btn("+ Thêm mới", "primary")
        btn_add.clicked.connect(self._open_add)
        btn_xl = self.make_btn("Xuất Excel")
        btn_xl.clicked.connect(self._export)
        self.add_action(btn_xl)
        self.add_action(btn_add)

        # Toolbar
        tb = QHBoxLayout()
        tb.setSpacing(8)
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm theo MSSV hoặc họ tên...")
        self.inp_search.setFixedHeight(34)
        self.inp_search.setStyleSheet(QSS_INPUT)
        self.inp_search.textChanged.connect(lambda: self._timer.start(400))

        self.cmb_khoa = self._combo(["Tất cả khoa"] + KHOA_LIST)
        self.cmb_tt   = self._combo(["Tất cả trạng thái"] + TRANG_THAI_SV)
        self.cmb_khoa.currentIndexChanged.connect(self._load)
        self.cmb_tt.currentIndexChanged.connect(self._load)

        tb.addWidget(self.inp_search, stretch=1)
        tb.addWidget(self.cmb_khoa)
        tb.addWidget(self.cmb_tt)
        self._root.addLayout(tb)

        # Table
        self.table = self.make_table(COLS)
        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(1, 170)
        self.table.setColumnWidth(2, 110)
        self.table.setColumnWidth(3, 130)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 100)
        self._root.addWidget(self.table)

        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        self._root.addWidget(self.lbl_count)

    def refresh(self):
        self._load()

    def _load(self):
        search = self.inp_search.text().strip()
        khoa   = self.cmb_khoa.currentText() if self.cmb_khoa.currentIndex() > 0 else ""
        tt     = self.cmb_tt.currentText()   if self.cmb_tt.currentIndex()   > 0 else ""
        self.run_async(
            lambda: self._ctrl._svc.get_list(search, khoa, tt),
            self._render,
        )

    def _render(self, data: dict):
        items = data.get("items", [])
        total = data.get("total", len(items))
        self.set_subtitle(f"Quản lý hồ sơ sinh viên")
        self.lbl_count.setText(f"Hiển thị {len(items)} / {total} sinh viên")
        self.table.setRowCount(len(items))

        for row, sv in enumerate(items):
            self.table.setItem(row, 0, self.cell(sv.get("mssv", "")))
            self.table.setItem(row, 1, self.cell(sv.get("ho_ten", ""), bold=True))
            self.table.setItem(row, 2, self.cell(sv.get("lop", "")))
            self.table.setItem(row, 3, self.cell(sv.get("khoa", "")))
            self.table.setItem(row, 4, self.cell(fmt_date(sv.get("ngay_sinh", ""))))
            self.table.setItem(row, 5, self.badge_cell(sv.get("trang_thai", "")))

            # Thao tác
            mssv = sv.get("mssv", "")
            w = QWidget()
            hl = QHBoxLayout(w)
            hl.setContentsMargins(4, 2, 4, 2)
            hl.setSpacing(4)
            for txt, fn, clr in [
                ("Sửa",  lambda _, m=mssv: self._open_edit(m), ACCENT),
                ("Xóa",  lambda _, m=mssv: self._delete(m),    DANGER),
            ]:
                b = QPushButton(txt)
                b.setFixedHeight(26)
                b.setCursor(Qt.CursorShape.PointingHandCursor)
                b.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {clr};
                        border: 1px solid {clr};
                        border-radius: 4px;
                        font-size: 11px;
                        padding: 0 8px;
                    }}
                    QPushButton:hover {{ background: {clr}; color: white; }}
                """)
                b.clicked.connect(fn)
                hl.addWidget(b)
            self.table.setCellWidget(row, 6, w)

    def _combo(self, items: list) -> QComboBox:
        c = QComboBox()
        c.addItems(items)
        c.setFixedHeight(34)
        c.setMinimumWidth(140)
        c.setStyleSheet(QSS_INPUT)
        return c

    def _open_add(self):
        dlg = StudentForm(on_save=self._load)
        dlg.exec()

    def _open_edit(self, mssv: str):
        raw = self._ctrl._svc.get_by_mssv(mssv)
        dlg = StudentForm(data=raw, on_save=self._load)
        dlg.exec()

    def _delete(self, mssv: str):
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Chuyển sinh viên {mssv} sang trạng thái 'Thôi học'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._ctrl.soft_delete(mssv, on_success=lambda _: self._load(), on_error=self._default_error)

    def _export(self):
        from controllers.report import ReportController
        path, _ = QFileDialog.getSaveFileName(self, "Lưu Excel", "sinh_vien.xlsx", "Excel (*.xlsx)")
        if path:
            ReportController().export_excel("sinhvien", path,
                on_success=lambda p: QMessageBox.information(self, "Thành công", f"Đã xuất:\n{p}"),
                on_error=self._default_error)


class StudentForm(QDialog):
    def __init__(self, data: dict | None = None, on_save=None):
        super().__init__()
        self._data    = data or {}
        self._on_save = on_save
        self._ctrl    = StudentController()
        self._is_edit = bool(data)
        self.setWindowTitle("Sửa sinh viên" if self._is_edit else "Thêm sinh viên")
        self.setFixedSize(520, 560)
        self.setStyleSheet(f"background: {PRIMARY}; color: {TEXT_LIGHT};")
        self._build()
        if data:
            self._fill(data)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)

        title = QLabel(self.windowTitle())
        title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_LIGHT};")
        root.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {BORDER};")
        root.addWidget(sep)

        grid = QGridLayout()
        grid.setSpacing(10)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 600;")
            l.setFixedWidth(120)
            return l

        def inp(ph=""):
            i = QLineEdit()
            i.setPlaceholderText(ph)
            i.setFixedHeight(34)
            i.setStyleSheet(QSS_INPUT)
            return i

        def cmb(items):
            c = QComboBox()
            c.addItems(items)
            c.setFixedHeight(34)
            c.setStyleSheet(QSS_INPUT)
            return c

        self.f_mssv   = inp("VD: SV001")
        self.f_hoten  = inp("Nguyễn Văn A")
        self.f_email  = inp("sv@abc.edu.vn")
        self.f_sdt    = inp("0901234567")
        self.f_lop    = inp("CNTT-K67")
        self.f_diachi = inp("Địa chỉ")
        self.f_ns     = QDateEdit()
        self.f_ns.setCalendarPopup(True)
        self.f_ns.setDate(QDate(2003, 1, 1))
        self.f_ns.setFixedHeight(34)
        self.f_ns.setStyleSheet(QSS_INPUT)
        self.f_gt  = cmb(GIOI_TINH)
        self.f_khoa = cmb(KHOA_LIST)
        self.f_tt  = cmb(TRANG_THAI_SV)

        rows = [
            ("Mã sinh viên *", self.f_mssv),
            ("Họ và tên *",    self.f_hoten),
            ("Ngày sinh",      self.f_ns),
            ("Giới tính",      self.f_gt),
            ("Email",          self.f_email),
            ("Số điện thoại",  self.f_sdt),
            ("Khoa *",         self.f_khoa),
            ("Lớp *",          self.f_lop),
            ("Địa chỉ",        self.f_diachi),
            ("Trạng thái",     self.f_tt),
        ]
        for i, (l, w) in enumerate(rows):
            grid.addWidget(lbl(l), i, 0)
            grid.addWidget(w, i, 1)

        root.addLayout(grid)
        root.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Hủy")
        btn_cancel.setFixedHeight(34)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_MUTED};
                border: 1px solid {BORDER}; border-radius: 6px;
                font-size: 13px; padding: 0 18px;
            }}
            QPushButton:hover {{ color: {TEXT_LIGHT}; border-color: {TEXT_MUTED}; }}
        """)
        btn_cancel.clicked.connect(self.reject)
        self.btn_save = QPushButton("Lưu")
        self.btn_save.setFixedHeight(34)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background: {HIGHLIGHT}; color: white;
                border: none; border-radius: 6px;
                font-size: 13px; font-weight: 700; padding: 0 24px;
            }}
            QPushButton:hover {{ background: #c73050; }}
            QPushButton:disabled {{ background: {BORDER}; color: {TEXT_MUTED}; }}
        """)
        self.btn_save.clicked.connect(self._save)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self.btn_save)
        root.addLayout(btn_row)

    def _fill(self, d: dict):
        self.f_mssv.setText(d.get("mssv", ""))
        self.f_mssv.setReadOnly(True)
        self.f_hoten.setText(d.get("ho_ten", ""))
        self.f_email.setText(d.get("email", ""))
        self.f_sdt.setText(d.get("sdt", ""))
        self.f_lop.setText(d.get("lop", ""))
        self.f_diachi.setText(d.get("dia_chi", ""))
        ns = d.get("ngay_sinh", "")
        if ns:
            self.f_ns.setDate(QDate.fromString(ns[:10], "yyyy-MM-dd"))
        for cmb, key in [(self.f_gt, "gioi_tinh"), (self.f_khoa, "khoa"), (self.f_tt, "trang_thai")]:
            idx = cmb.findText(d.get(key, ""))
            if idx >= 0:
                cmb.setCurrentIndex(idx)

    def _collect(self) -> dict:
        return {
            "mssv":       self.f_mssv.text().strip(),
            "ho_ten":     self.f_hoten.text().strip(),
            "ngay_sinh":  self.f_ns.date().toString("yyyy-MM-dd"),
            "gioi_tinh":  self.f_gt.currentText(),
            "email":      self.f_email.text().strip(),
            "sdt":        self.f_sdt.text().strip(),
            "khoa":       self.f_khoa.currentText(),
            "lop":        self.f_lop.text().strip(),
            "dia_chi":    self.f_diachi.text().strip(),
            "trang_thai": self.f_tt.currentText(),
        }

    def _save(self):
        data = self._collect()
        self.btn_save.setEnabled(False)
        self.btn_save.setText("Đang lưu...")

        def ok(_):
            if self._on_save:
                self._on_save()
            self.accept()

        def err(msg):
            self.btn_save.setEnabled(True)
            self.btn_save.setText("Lưu")
            QMessageBox.warning(self, "Lỗi", msg)

        if self._is_edit:
            self._ctrl.update(data["mssv"], data, on_success=ok, on_error=err)
        else:
            self._ctrl.create(data, on_success=ok, on_error=err)