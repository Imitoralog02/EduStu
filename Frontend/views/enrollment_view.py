from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLineEdit, QComboBox, QPushButton,
    QLabel, QFrame, QDialog, QGridLayout, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from views.base_view import BaseView, QSS_INPUT, QSS_BTN_PRIMARY, QSS_BTN_DANGER
from controllers.course import EnrollmentController, CourseController
from controllers.student import StudentController
from models.student import Student
from models.course import Enrollment
from utils.config import (
    PRIMARY, SECONDARY, BORDER, TEXT_LIGHT, TEXT_MUTED,
    ACCENT, HIGHLIGHT, DANGER, SUCCESS, WARNING, HOC_KY_LIST,
)

COLS = ["Mã HP", "Tên học phần", "Học kỳ", "Thao tác"]


class EnrollmentView(BaseView):
    PAGE_TITLE = "Đăng ký học phần"
    PAGE_SUB   = "Quản lý đăng ký học phần của sinh viên"

    def __init__(self):
        self._ctrl    = EnrollmentController()
        self._sv_ctrl = StudentController()
        self._student: Student | None = None
        self._enrollments: list[Enrollment] = []
        super().__init__()

    def build_ui(self):
        # ── Thanh tìm kiếm sinh viên ──────────────────────────────────────
        sr = QHBoxLayout()
        sr.setSpacing(8)

        self.inp_mssv = QLineEdit()
        self.inp_mssv.setPlaceholderText("Nhập MSSV rồi nhấn Enter hoặc nhấn Tìm kiếm...")
        self.inp_mssv.setFixedHeight(36)
        self.inp_mssv.setStyleSheet(QSS_INPUT)
        self.inp_mssv.returnPressed.connect(self._search)

        self.cmb_hk = QComboBox()
        self.cmb_hk.addItems(["Tất cả học kỳ"] + HOC_KY_LIST)
        self.cmb_hk.setFixedHeight(36)
        self.cmb_hk.setMinimumWidth(160)
        self.cmb_hk.setStyleSheet(QSS_INPUT)
        self.cmb_hk.currentIndexChanged.connect(self._reload)

        btn_search = QPushButton("Tìm kiếm")
        btn_search.setFixedHeight(36)
        btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_search.setStyleSheet(
            f"QPushButton{{background:{ACCENT};color:{TEXT_LIGHT};border:none;"
            f"border-radius:6px;font-size:13px;font-weight:600;padding:0 16px;}}"
            f"QPushButton:hover{{background:#1a4a80;}}"
        )
        btn_search.clicked.connect(self._search)

        sr.addWidget(self.inp_mssv, stretch=1)
        sr.addWidget(self.cmb_hk)
        sr.addWidget(btn_search)
        self._root.addLayout(sr)

        # ── Layout chính: profile bên trái, bảng bên phải ────────────────
        main = QHBoxLayout()
        main.setSpacing(14)

        # Profile card
        self.profile = self._make_profile_card()
        main.addWidget(self.profile, stretch=0)

        # Phần phải: nút + bảng + thống kê
        right = QVBoxLayout()
        right.setSpacing(10)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_dky = self.make_btn("+ Đăng ký học phần", "primary")
        self.btn_dky.clicked.connect(self._open_dky)
        btn_row.addWidget(self.btn_dky)
        right.addLayout(btn_row)

        self.table = self.make_table(COLS)
        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(1, 260)
        self.table.setColumnWidth(2, 150)
        right.addWidget(self.table)

        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet(
            f"background:{SECONDARY};border-radius:6px;padding:8px 14px;"
            f"font-size:12px;color:{TEXT_MUTED};"
        )
        right.addWidget(self.lbl_count)

        main.addLayout(right, stretch=1)
        self._root.addLayout(main)

    # ── Profile card ──────────────────────────────────────────────────────
    def _make_profile_card(self) -> QFrame:
        f = QFrame()
        f.setFixedWidth(210)
        f.setStyleSheet(
            f"QFrame{{background:{SECONDARY};border:1px solid {BORDER};border-radius:10px;}}"
        )
        lay = QVBoxLayout(f)
        lay.setContentsMargins(16, 20, 16, 20)
        lay.setSpacing(6)
        lay.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.av = QLabel("?")
        self.av.setFixedSize(52, 52)
        self.av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.av.setStyleSheet(
            f"background:{ACCENT};color:{TEXT_LIGHT};border-radius:26px;"
            f"font-size:18px;font-weight:700;border:none;"
        )

        self.p_name = QLabel("Chưa chọn sinh viên")
        self.p_name.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.p_name.setStyleSheet(f"color:{TEXT_LIGHT};border:none;")
        self.p_name.setWordWrap(True)
        self.p_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.p_mssv = QLabel("")
        self.p_mssv.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;border:none;")
        self.p_mssv.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.p_lop = QLabel("")
        self.p_lop.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;border:none;")
        self.p_lop.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{BORDER};")

        self.p_vals: dict[str, QLabel] = {}
        lay.addWidget(self.av, alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.p_name)
        lay.addWidget(self.p_mssv)
        lay.addWidget(self.p_lop)
        lay.addWidget(sep)

        for key, unit in [("Đã đăng ký", "học phần"), ("Học kỳ xem", "")]:
            row = QHBoxLayout()
            k = QLabel(key)
            k.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;border:none;")
            v = QLabel("—")
            v.setStyleSheet(
                f"color:{TEXT_LIGHT};font-size:12px;font-weight:600;border:none;"
            )
            v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.p_vals[key] = v
            row.addWidget(k)
            row.addStretch()
            row.addWidget(v)
            w = QWidget()
            w.setLayout(row)
            lay.addWidget(w)

        lay.addStretch()
        return f

    # ── Tìm kiếm sinh viên ───────────────────────────────────────────────
    def _search(self):
        mssv = self.inp_mssv.text().strip()
        if not mssv:
            QMessageBox.information(self, "Thông báo", "Vui lòng nhập MSSV.")
            return
        self._sv_ctrl.load_one(mssv, on_success=self._on_sv, on_error=self._default_error)

    def _on_sv(self, sv: Student):
        self._student = sv
        self.av.setText(sv.avatar_text)
        self.p_name.setText(sv.ho_ten)
        self.p_mssv.setText(sv.mssv)
        self.p_lop.setText(f"{sv.lop} · {sv.khoa}")
        self._reload()

    # ── Tải danh sách đăng ký ────────────────────────────────────────────
    def _reload(self):
        if not self._student:
            return
        hk = self.cmb_hk.currentText()
        hk_param = "" if hk == "Tất cả học kỳ" else hk
        self._ctrl.load_by_student(
            self._student.mssv, hk_param,
            on_success=self._render,
            on_error=self._default_error,
        )

    def _render(self, items: list[Enrollment]):
        self._enrollments = items
        self.table.setRowCount(len(items))

        for row, e in enumerate(items):
            self.table.setItem(row, 0, self.cell(e.ma_hp))
            self.table.setItem(row, 1, self.cell(e.ten_hp, bold=True))
            self.table.setItem(row, 2, self.cell(e.hoc_ky))

            # Nút Hủy đăng ký
            w = QWidget()
            hl = QHBoxLayout(w)
            hl.setContentsMargins(4, 2, 4, 2)
            hl.setSpacing(4)
            btn_huy = QPushButton("Hủy ĐK")
            btn_huy.setFixedHeight(26)
            btn_huy.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_huy.setStyleSheet(
                f"QPushButton{{background:transparent;color:{DANGER};"
                f"border:1px solid {DANGER};border-radius:4px;font-size:11px;padding:0 8px;}}"
                f"QPushButton:hover{{background:{DANGER};color:white;}}"
            )
            btn_huy.clicked.connect(lambda _, eid=e.id: self._cancel(eid))
            hl.addWidget(btn_huy)
            hl.addStretch()
            self.table.setCellWidget(row, 3, w)

        # Cập nhật profile card
        hk_text = self.cmb_hk.currentText()
        self.p_vals["Đã đăng ký"].setText(str(len(items)))
        self.p_vals["Học kỳ xem"].setText(
            hk_text if hk_text != "Tất cả học kỳ" else "Tất cả"
        )
        self.lbl_count.setText(
            f"Sinh viên {self._student.mssv} đang đăng ký "
            f"{len(items)} học phần"
            + (f" trong {hk_text}" if hk_text != "Tất cả học kỳ" else "")
        )

    # ── Đăng ký học phần mới ─────────────────────────────────────────────
    def _open_dky(self):
        if not self._student:
            QMessageBox.information(
                self, "Thông báo", "Vui lòng tìm kiếm sinh viên trước."
            )
            return
        dlg = EnrollForm(mssv=self._student.mssv, on_save=self._reload)
        dlg.exec()

    # ── Hủy đăng ký ──────────────────────────────────────────────────────
    def _cancel(self, enrollment_id: int):
        reply = QMessageBox.question(
            self, "Xác nhận hủy",
            "Bạn có chắc muốn hủy đăng ký học phần này không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._ctrl.cancel(
                enrollment_id,
                on_success=lambda _: self._reload(),
                on_error=self._default_error,
            )


# ══════════════════════════════════════════════════════════════════════════════
# Dialog: Đăng ký học phần
# ══════════════════════════════════════════════════════════════════════════════
class EnrollForm(QDialog):
    def __init__(self, mssv: str, on_save=None):
        super().__init__()
        self._mssv    = mssv
        self._on_save = on_save
        self._ctrl    = EnrollmentController()
        self._c_ctrl  = CourseController()
        self._courses: list = []

        self.setWindowTitle(f"Đăng ký học phần — {mssv}")
        self.setFixedSize(460, 320)
        self.setStyleSheet(f"background:{PRIMARY};color:{TEXT_LIGHT};")
        self._build()
        self._load_courses()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)

        title = QLabel(f"Đăng ký học phần cho: {self._mssv}")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{TEXT_LIGHT};")
        root.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{BORDER};")
        root.addWidget(sep)

        grid = QGridLayout()
        grid.setSpacing(12)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet(
                f"color:{TEXT_MUTED};font-size:11px;font-weight:600;"
            )
            l.setFixedWidth(110)
            return l

        # Chọn học phần
        self.cmb_hp = QComboBox()
        self.cmb_hp.setFixedHeight(34)
        self.cmb_hp.setStyleSheet(QSS_INPUT)
        self.cmb_hp.setPlaceholderText("Đang tải danh sách...")

        # Tìm nhanh học phần
        self.inp_filter = QLineEdit()
        self.inp_filter.setPlaceholderText("Lọc nhanh tên / mã HP...")
        self.inp_filter.setFixedHeight(34)
        self.inp_filter.setStyleSheet(QSS_INPUT)
        self.inp_filter.textChanged.connect(self._filter_courses)

        # Học kỳ
        self.cmb_hk = QComboBox()
        self.cmb_hk.addItems(HOC_KY_LIST)
        self.cmb_hk.setFixedHeight(34)
        self.cmb_hk.setStyleSheet(QSS_INPUT)

        # Thông tin học phần đã chọn
        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet(
            f"color:{ACCENT};font-size:12px;border:none;"
        )
        self.cmb_hp.currentIndexChanged.connect(self._update_info)

        grid.addWidget(lbl("Lọc học phần"), 0, 0)
        grid.addWidget(self.inp_filter,      0, 1)
        grid.addWidget(lbl("Học phần *"),    1, 0)
        grid.addWidget(self.cmb_hp,          1, 1)
        grid.addWidget(lbl("Thông tin"),     2, 0)
        grid.addWidget(self.lbl_info,        2, 1)
        grid.addWidget(lbl("Học kỳ *"),      3, 0)
        grid.addWidget(self.cmb_hk,          3, 1)

        root.addLayout(grid)
        root.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        bc = QPushButton("Hủy")
        bc.setFixedHeight(34)
        bc.setCursor(Qt.CursorShape.PointingHandCursor)
        bc.setStyleSheet(
            f"QPushButton{{background:transparent;color:{TEXT_MUTED};"
            f"border:1px solid {BORDER};border-radius:6px;padding:0 16px;}}"
            f"QPushButton:hover{{color:{TEXT_LIGHT};}}"
        )
        bc.clicked.connect(self.reject)

        self.bs = QPushButton("Đăng ký")
        self.bs.setFixedHeight(34)
        self.bs.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bs.setStyleSheet(
            f"QPushButton{{background:{HIGHLIGHT};color:white;border:none;"
            f"border-radius:6px;font-size:13px;font-weight:700;padding:0 24px;}}"
            f"QPushButton:hover{{background:#c73050;}}"
            f"QPushButton:disabled{{background:{BORDER};color:{TEXT_MUTED};}}"
        )
        self.bs.clicked.connect(self._save)
        btn_row.addWidget(bc)
        btn_row.addWidget(self.bs)
        root.addLayout(btn_row)

    def _load_courses(self):
        self._c_ctrl.load_list(
            on_success=self._on_courses,
            on_error=lambda msg: self.cmb_hp.addItem(f"Lỗi: {msg}"),
        )

    def _on_courses(self, courses):
        self._courses = courses
        self._populate_combo(courses)

    def _populate_combo(self, courses):
        self.cmb_hp.clear()
        for c in courses:
            self.cmb_hp.addItem(f"{c.ma_hp} — {c.ten_hp} ({c.so_tin_chi} TC)", c)
        self._update_info()

    def _filter_courses(self, text: str):
        keyword = text.lower()
        filtered = [
            c for c in self._courses
            if keyword in c.ma_hp.lower() or keyword in c.ten_hp.lower()
        ]
        self._populate_combo(filtered)

    def _update_info(self):
        c = self.cmb_hp.currentData()
        if c:
            self.lbl_info.setText(
                f"Giảng viên: {c.giao_vien}   ·   {c.so_tin_chi} tín chỉ"
            )
        else:
            self.lbl_info.setText("")

    def _save(self):
        c = self.cmb_hp.currentData()
        if not c:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn học phần.")
            return
        self.bs.setEnabled(False)
        self.bs.setText("Đang đăng ký...")

        def ok(_):
            if self._on_save:
                self._on_save()
            self.accept()

        def err(msg):
            self.bs.setEnabled(True)
            self.bs.setText("Đăng ký")
            QMessageBox.warning(self, "Lỗi", msg)

        self._ctrl.enroll(
            self._mssv,
            c.ma_hp,
            self.cmb_hk.currentText(),
            on_success=ok,
            on_error=err,
        )
