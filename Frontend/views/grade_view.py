from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLineEdit, QComboBox, QPushButton,
    QLabel, QFrame, QDialog, QGridLayout, QDoubleSpinBox,
    QMessageBox, QWidget, QTableWidget, QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from views.base_view import BaseView, QSS_INPUT, QSS_TABLE
from controllers.grade import GradeController
from controllers.student import StudentController
from models.student import Student
from models.grade import Grade
from utils.config import (
    PRIMARY, SECONDARY, BORDER, TEXT_LIGHT, TEXT_MUTED,
    ACCENT, HIGHLIGHT, DANGER, SUCCESS, WARNING, HOC_KY_LIST,
)
from utils.helpers import fmt_gpa, badge_color

# Thêm cột "Thao tác" để chứa nút Sửa
COLS = ["Mã HP", "Tên học phần", "TC", "Giữa kỳ", "Cuối kỳ", "Tổng kết", "Xếp loại", "Kết quả", "Thao tác"]


class GradeView(BaseView):
    PAGE_TITLE = "Điểm số"
    PAGE_SUB   = "Tra cứu và nhập điểm sinh viên"

    def __init__(self):
        self._ctrl    = GradeController()
        self._sv_ctrl = StudentController()
        self._student: Student | None = None
        # Lưu id của từng dòng để sửa điểm
        self._grade_ids: list[int] = []
        self._grade_data_cache: list[dict] = []
        super().__init__()

    def build_ui(self):
        # ── Thanh tìm kiếm ───────────────────────────────────────────────
        sr = QHBoxLayout()
        sr.setSpacing(8)
        self.inp_mssv = QLineEdit()
        self.inp_mssv.setPlaceholderText("Nhập MSSV rồi nhấn Enter...")
        self.inp_mssv.setFixedHeight(36)
        self.inp_mssv.setStyleSheet(QSS_INPUT)
        self.inp_mssv.returnPressed.connect(self._search)

        self.cmb_hk = QComboBox()
        self.cmb_hk.addItems(["Tất cả học kỳ"] + HOC_KY_LIST)
        self.cmb_hk.setFixedHeight(36)
        self.cmb_hk.setMinimumWidth(150)
        self.cmb_hk.setStyleSheet(QSS_INPUT)
        self.cmb_hk.currentIndexChanged.connect(self._reload)

        btn_search = QPushButton("Xem bảng điểm")
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

        # ── Layout chính ──────────────────────────────────────────────────
        main = QHBoxLayout()
        main.setSpacing(14)

        # Profile card bên trái
        self.profile = self._make_profile_card()
        main.addWidget(self.profile, stretch=0)

        # Phần phải: nút hành động + bảng + tổng kết
        right = QVBoxLayout()
        right.setSpacing(10)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_nhap = self.make_btn("+ Nhập điểm", "primary")
        self.btn_nhap.clicked.connect(self._open_nhap)
        btn_row.addWidget(self.btn_nhap)
        right.addLayout(btn_row)

        self.table = self.make_table(COLS)
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 185)
        self.table.setColumnWidth(2, 36)
        self.table.setColumnWidth(3, 76)
        self.table.setColumnWidth(4, 76)
        self.table.setColumnWidth(5, 76)
        self.table.setColumnWidth(6, 80)
        self.table.setColumnWidth(7, 72)
        right.addWidget(self.table)

        self.lbl_summary = QLabel("")
        self.lbl_summary.setStyleSheet(
            f"background:{SECONDARY};border-radius:6px;padding:8px 14px;"
            f"font-size:12px;color:{TEXT_MUTED};"
        )
        right.addWidget(self.lbl_summary)
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

        self.p_name = QLabel("—")
        self.p_name.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.p_name.setStyleSheet(f"color:{TEXT_LIGHT};border:none;")
        self.p_name.setWordWrap(True)
        self.p_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.p_lop = QLabel("")
        self.p_lop.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;border:none;")
        self.p_lop.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{BORDER};")

        self.p_vals: dict[str, QLabel] = {}
        lay.addWidget(self.av, alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.p_name)
        lay.addWidget(self.p_lop)
        lay.addWidget(sep)

        for key in ["GPA tích lũy", "Xếp loại", "TC tích lũy", "Cảnh báo"]:
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

        # Nút GPA chi tiết
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color:{BORDER};margin-top:4px;")
        lay.addWidget(sep2)

        self.btn_gpa_detail = QPushButton("Xem GPA chi tiết")
        self.btn_gpa_detail.setFixedHeight(30)
        self.btn_gpa_detail.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_gpa_detail.setStyleSheet(
            f"QPushButton{{background:transparent;color:{ACCENT};"
            f"border:1px solid {ACCENT};border-radius:5px;font-size:11px;}}"
            f"QPushButton:hover{{background:{ACCENT};color:white;}}"
        )
        self.btn_gpa_detail.clicked.connect(self._open_gpa_detail)
        lay.addWidget(self.btn_gpa_detail)

        lay.addStretch()
        return f

    # ── Tìm kiếm sinh viên ───────────────────────────────────────────────
    def _search(self):
        mssv = self.inp_mssv.text().strip()
        if not mssv:
            return
        self._sv_ctrl.load_one(
            mssv, on_success=self._on_sv, on_error=self._default_error
        )

    def _on_sv(self, sv: Student):
        self._student = sv
        self.av.setText(sv.avatar_text)
        self.p_name.setText(sv.ho_ten)
        self.p_lop.setText(f"{sv.lop} · {sv.khoa}")
        self._reload()

    # ── Tải bảng điểm ────────────────────────────────────────────────────
    def _reload(self):
        if not self._student:
            return
        hk = self.cmb_hk.currentText()
        hk_param = "" if hk == "Tất cả học kỳ" else hk
        self.run_async(
            lambda: self._ctrl._svc.get_transcript(self._student.mssv, hk_param),
            self._render,
        )

    def _render(self, data: dict):
        items = data.get("diem_list", [])
        self._grade_data_cache = items
        self._grade_ids = [d.get("id", 0) for d in items]
        self.table.setRowCount(len(items))

        for row, d in enumerate(items):
            g = Grade.from_dict(d)
            self.table.setItem(row, 0, self.cell(g.ma_hp))
            self.table.setItem(row, 1, self.cell(g.ten_hp, bold=True))
            self.table.setItem(
                row, 2,
                self.cell(str(g.so_tin_chi), align=Qt.AlignmentFlag.AlignCenter),
            )
            self.table.setItem(
                row, 3,
                self.cell(g.diem_gk_display, align=Qt.AlignmentFlag.AlignCenter),
            )
            self.table.setItem(
                row, 4,
                self.cell(g.diem_ck_display, align=Qt.AlignmentFlag.AlignCenter),
            )
            tong_item = self.cell(
                g.tong_ket_display,
                align=Qt.AlignmentFlag.AlignCenter,
                bold=True,
                color=SUCCESS if g.dat else DANGER,
            )
            self.table.setItem(row, 5, tong_item)
            # Xếp loại môn
            xl_mon = _xep_loai_mon(g.tong_ket)
            self.table.setItem(row, 6, self.cell(xl_mon))
            self.table.setItem(row, 7, self.badge_cell(g.ket_qua))

            # Nút Sửa điểm
            grade_id = d.get("id", 0)
            w = QWidget()
            hl = QHBoxLayout(w)
            hl.setContentsMargins(4, 2, 4, 2)
            btn_sua = QPushButton("Sửa")
            btn_sua.setFixedHeight(26)
            btn_sua.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_sua.setStyleSheet(
                f"QPushButton{{background:transparent;color:{ACCENT};"
                f"border:1px solid {ACCENT};border-radius:4px;"
                f"font-size:11px;padding:0 8px;}}"
                f"QPushButton:hover{{background:{ACCENT};color:white;}}"
            )
            btn_sua.clicked.connect(
                lambda _, gid=grade_id, gk=g.diem_gk, ck=g.diem_ck, mhp=g.ma_hp:
                    self._open_sua(gid, mhp, gk, ck)
            )
            hl.addWidget(btn_sua)
            hl.addStretch()
            self.table.setCellWidget(row, 8, w)

        # Cập nhật profile card
        gpa_tl = data.get("gpa_tich_luy")
        tc_dat = data.get("tin_chi_dat", 0)
        tc_dk  = data.get("tin_chi_dang_ky", 0)
        xl     = data.get("xep_loai", "—")
        cb     = data.get("canh_bao", "")

        self.p_vals["GPA tích lũy"].setText(fmt_gpa(gpa_tl))
        self.p_vals["Xếp loại"].setText(xl)
        self.p_vals["TC tích lũy"].setText(f"{tc_dat}/{tc_dk}")
        cb_lbl = cb or "Bình thường"
        self.p_vals["Cảnh báo"].setText(cb_lbl)
        self.p_vals["Cảnh báo"].setStyleSheet(
            f"color:{DANGER};font-size:12px;font-weight:600;border:none;" if cb
            else f"color:{SUCCESS};font-size:12px;font-weight:600;border:none;"
        )
        self.lbl_summary.setText(
            f"GPA kỳ: {fmt_gpa(data.get('gpa_ky'))}   ·   "
            f"TC đạt: {tc_dat}/{tc_dk}   ·   Xếp loại: {xl}"
        )

    # ── Nhập điểm mới ────────────────────────────────────────────────────
    def _open_nhap(self):
        if not self._student:
            QMessageBox.information(
                self, "Thông báo", "Vui lòng tìm kiếm sinh viên trước."
            )
            return
        dlg = GradeForm(mssv=self._student.mssv, on_save=self._reload)
        dlg.exec()

    # ── Sửa điểm đã có ───────────────────────────────────────────────────
    def _open_sua(self, grade_id: int, ma_hp: str, diem_gk: float, diem_ck: float):
        if grade_id == 0:
            QMessageBox.warning(
                self, "Không thể sửa",
                "Không tìm thấy ID của điểm này. "
                "Có thể dữ liệu từ API chưa trả về id.",
            )
            return
        dlg = GradeEditForm(
            grade_id=grade_id,
            ma_hp=ma_hp,
            diem_gk=diem_gk,
            diem_ck=diem_ck,
            on_save=self._reload,
        )
        dlg.exec()

    # ── GPA chi tiết ─────────────────────────────────────────────────────
    def _open_gpa_detail(self):
        if not self._student:
            QMessageBox.information(
                self, "Thông báo", "Vui lòng tìm kiếm sinh viên trước."
            )
            return
        dlg = GpaDetailDialog(
            mssv=self._student.mssv,
            ho_ten=self._student.ho_ten,
        )
        dlg.exec()


# ══════════════════════════════════════════════════════════════════════════════
# Dialog: Nhập điểm mới
# ══════════════════════════════════════════════════════════════════════════════
class GradeForm(QDialog):
    def __init__(self, mssv: str, on_save=None):
        super().__init__()
        self._mssv    = mssv
        self._on_save = on_save
        self._ctrl    = GradeController()
        self.setWindowTitle(f"Nhập điểm — {mssv}")
        self.setFixedSize(380, 300)
        self.setStyleSheet(f"background:{PRIMARY};color:{TEXT_LIGHT};")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        title = QLabel(f"Nhập điểm cho: {self._mssv}")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        root.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{BORDER};")
        root.addWidget(sep)

        grid = QGridLayout()
        grid.setSpacing(10)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet(
                f"color:{TEXT_MUTED};font-size:11px;font-weight:600;"
            )
            l.setFixedWidth(110)
            return l

        def spin():
            s = QDoubleSpinBox()
            s.setRange(0, 10)
            s.setSingleStep(0.5)
            s.setDecimals(1)
            s.setFixedHeight(34)
            s.setStyleSheet(QSS_INPUT)
            return s

        self.f_mahp = QLineEdit()
        self.f_mahp.setPlaceholderText("VD: CS101")
        self.f_mahp.setFixedHeight(34)
        self.f_mahp.setStyleSheet(QSS_INPUT)

        self.f_hk = QComboBox()
        self.f_hk.addItems(HOC_KY_LIST)
        self.f_hk.setFixedHeight(34)
        self.f_hk.setStyleSheet(QSS_INPUT)

        self.f_gk = spin()
        self.f_ck = spin()
        self.f_gk.valueChanged.connect(self._update_tong)
        self.f_ck.valueChanged.connect(self._update_tong)

        self.lbl_tong = QLabel("Tổng kết: 0.00")
        self.lbl_tong.setStyleSheet(
            f"color:{ACCENT};font-size:13px;font-weight:600;"
        )

        for i, (l, w) in enumerate([
            ("Mã HP *",      self.f_mahp),
            ("Học kỳ *",     self.f_hk),
            ("Điểm GK (40%)", self.f_gk),
            ("Điểm CK (60%)", self.f_ck),
        ]):
            grid.addWidget(lbl(l), i, 0)
            grid.addWidget(w, i, 1)

        root.addLayout(grid)
        root.addWidget(self.lbl_tong)
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

        self.bs = QPushButton("Lưu điểm")
        self.bs.setFixedHeight(34)
        self.bs.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bs.setStyleSheet(
            f"QPushButton{{background:{HIGHLIGHT};color:white;border:none;"
            f"border-radius:6px;font-weight:700;padding:0 20px;}}"
            f"QPushButton:hover{{background:#c73050;}}"
        )
        self.bs.clicked.connect(self._save)
        btn_row.addWidget(bc)
        btn_row.addWidget(self.bs)
        root.addLayout(btn_row)

    def _update_tong(self):
        from utils.config import TRONG_SO_GK, TRONG_SO_CK
        t = round(self.f_gk.value() * TRONG_SO_GK + self.f_ck.value() * TRONG_SO_CK, 2)
        clr = SUCCESS if t >= 5.0 else DANGER
        self.lbl_tong.setText(f"Tổng kết: {t:.2f}")
        self.lbl_tong.setStyleSheet(f"color:{clr};font-size:13px;font-weight:600;")

    def _save(self):
        self.bs.setEnabled(False)

        def ok(_):
            if self._on_save:
                self._on_save()
            self.accept()

        def err(msg):
            self.bs.setEnabled(True)
            QMessageBox.warning(self, "Lỗi", msg)

        self._ctrl.create_grade(
            self._mssv,
            self.f_mahp.text().strip(),
            self.f_hk.currentText(),
            self.f_gk.value(),
            self.f_ck.value(),
            on_success=ok,
            on_error=err,
        )


# ══════════════════════════════════════════════════════════════════════════════
# Dialog: Sửa điểm đã nhập
# ══════════════════════════════════════════════════════════════════════════════
class GradeEditForm(QDialog):
    def __init__(
        self,
        grade_id: int,
        ma_hp: str,
        diem_gk: float,
        diem_ck: float,
        on_save=None,
    ):
        super().__init__()
        self._grade_id = grade_id
        self._on_save  = on_save
        self._ctrl     = GradeController()
        self.setWindowTitle(f"Sửa điểm — {ma_hp}")
        self.setFixedSize(380, 260)
        self.setStyleSheet(f"background:{PRIMARY};color:{TEXT_LIGHT};")
        self._build(ma_hp, diem_gk, diem_ck)

    def _build(self, ma_hp: str, diem_gk: float, diem_ck: float):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        title = QLabel(f"Sửa điểm học phần: {ma_hp}")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{TEXT_LIGHT};")
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

        def spin(val: float):
            s = QDoubleSpinBox()
            s.setRange(0, 10)
            s.setSingleStep(0.5)
            s.setDecimals(1)
            s.setValue(val)
            s.setFixedHeight(34)
            s.setStyleSheet(QSS_INPUT)
            return s

        self.f_gk = spin(diem_gk)
        self.f_ck = spin(diem_ck)
        self.f_gk.valueChanged.connect(self._update_tong)
        self.f_ck.valueChanged.connect(self._update_tong)

        self.lbl_tong = QLabel("")
        self.lbl_tong.setStyleSheet(f"color:{ACCENT};font-size:13px;font-weight:600;")

        grid.addWidget(lbl("Điểm GK (40%)"), 0, 0)
        grid.addWidget(self.f_gk,            0, 1)
        grid.addWidget(lbl("Điểm CK (60%)"), 1, 0)
        grid.addWidget(self.f_ck,            1, 1)
        grid.addWidget(lbl("Tổng kết"),      2, 0)
        grid.addWidget(self.lbl_tong,        2, 1)

        root.addLayout(grid)
        self._update_tong()
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

        self.bs = QPushButton("Lưu thay đổi")
        self.bs.setFixedHeight(34)
        self.bs.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bs.setStyleSheet(
            f"QPushButton{{background:{HIGHLIGHT};color:white;border:none;"
            f"border-radius:6px;font-weight:700;padding:0 20px;}}"
            f"QPushButton:hover{{background:#c73050;}}"
        )
        self.bs.clicked.connect(self._save)
        btn_row.addWidget(bc)
        btn_row.addWidget(self.bs)
        root.addLayout(btn_row)

    def _update_tong(self):
        from utils.config import TRONG_SO_GK, TRONG_SO_CK
        t = round(self.f_gk.value() * TRONG_SO_GK + self.f_ck.value() * TRONG_SO_CK, 2)
        clr = SUCCESS if t >= 5.0 else DANGER
        self.lbl_tong.setText(f"{t:.2f}  ({_xep_loai_mon(t)})")
        self.lbl_tong.setStyleSheet(f"color:{clr};font-size:13px;font-weight:600;")

    def _save(self):
        self.bs.setEnabled(False)
        self.bs.setText("Đang lưu...")

        def ok(_):
            if self._on_save:
                self._on_save()
            self.accept()

        def err(msg):
            self.bs.setEnabled(True)
            self.bs.setText("Lưu thay đổi")
            QMessageBox.warning(self, "Lỗi", msg)

        self._ctrl.update_grade(
            self._grade_id,
            self.f_gk.value(),
            self.f_ck.value(),
            on_success=ok,
            on_error=err,
        )


# ══════════════════════════════════════════════════════════════════════════════
# Dialog: GPA chi tiết theo từng học kỳ
# ══════════════════════════════════════════════════════════════════════════════
class GpaDetailDialog(QDialog):
    def __init__(self, mssv: str, ho_ten: str):
        super().__init__()
        self._mssv   = mssv
        self._ctrl   = GradeController()
        self.setWindowTitle(f"GPA chi tiết — {ho_ten} ({mssv})")
        self.setFixedSize(560, 460)
        self.setStyleSheet(f"background:{PRIMARY};color:{TEXT_LIGHT};")
        self._build(ho_ten)
        self._load()

    def _build(self, ho_ten: str):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        # Tiêu đề
        title = QLabel(f"GPA chi tiết: {ho_ten}")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{TEXT_LIGHT};")
        root.addWidget(title)

        # Tổng quan — 3 card ngang
        overview = QHBoxLayout()
        overview.setSpacing(10)
        colors = [ACCENT, SUCCESS, WARNING]
        labels = ["GPA tích lũy", "TC tích lũy", "Xếp loại"]
        self._ov_vals: list[QLabel] = []
        for lbl_txt, clr in zip(labels, colors):
            card = QFrame()
            card.setStyleSheet(
                f"QFrame{{background:{SECONDARY};border:1px solid {BORDER};"
                f"border-top:3px solid {clr};border-radius:8px;}}"
            )
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 10, 14, 10)
            cl.setSpacing(2)
            lbl = QLabel(lbl_txt)
            lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;border:none;")
            val = QLabel("...")
            val.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            val.setStyleSheet(f"color:{clr};border:none;")
            cl.addWidget(lbl)
            cl.addWidget(val)
            self._ov_vals.append(val)
            overview.addWidget(card)
        root.addLayout(overview)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{BORDER};")
        root.addWidget(sep)

        # Bảng GPA từng học kỳ
        lbl_tbl = QLabel("GPA từng học kỳ")
        lbl_tbl.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lbl_tbl.setStyleSheet(f"color:{TEXT_LIGHT};")
        root.addWidget(lbl_tbl)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Học kỳ", "GPA kỳ", "TC đạt", "Xếp loại"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setStyleSheet(QSS_TABLE)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.setColumnWidth(0, 160)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 80)
        root.addWidget(self.table)

        # Cảnh báo
        self.lbl_canh_bao = QLabel("")
        self.lbl_canh_bao.setStyleSheet(
            f"color:{DANGER};font-size:12px;font-weight:600;"
            f"background:rgba(231,76,60,0.12);border-radius:6px;padding:6px 12px;"
        )
        self.lbl_canh_bao.setWordWrap(True)
        self.lbl_canh_bao.hide()
        root.addWidget(self.lbl_canh_bao)

        btn_close = QPushButton("Đóng")
        btn_close.setFixedHeight(34)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(
            f"QPushButton{{background:transparent;color:{TEXT_MUTED};"
            f"border:1px solid {BORDER};border-radius:6px;padding:0 24px;}}"
            f"QPushButton:hover{{color:{TEXT_LIGHT};}}"
        )
        btn_close.clicked.connect(self.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        root.addLayout(btn_row)

    def _load(self):
        self._ctrl.load_gpa(
            self._mssv,
            on_success=self._render,
            on_error=lambda msg: self._ov_vals[0].setText("Lỗi"),
        )

    def _render(self, data: dict):
        # Tổng quan
        gpa_tl = data.get("gpa_tich_luy")
        tc_dat = data.get("tin_chi_dat", 0)
        tc_dk  = data.get("tin_chi_dang_ky", 0)
        xl     = data.get("xep_loai", "—")
        cb     = data.get("canh_bao", "")

        self._ov_vals[0].setText(fmt_gpa(gpa_tl))
        self._ov_vals[1].setText(f"{tc_dat}/{tc_dk}")
        self._ov_vals[2].setText(xl)

        # Cảnh báo học vụ
        if cb:
            self.lbl_canh_bao.setText(f"⚠  {cb}")
            self.lbl_canh_bao.show()

        # Bảng theo kỳ
        by_ky: list[dict] = data.get("by_ky", [])
        self.table.setRowCount(len(by_ky))
        for row, ky in enumerate(by_ky):
            gpa_ky  = ky.get("gpa") or ky.get("gpa_ky")
            tc_ky   = ky.get("tin_chi_dat", ky.get("tin_chi", 0))
            xl_ky   = ky.get("xep_loai", _xep_loai_gpa(gpa_ky))
            gpa_str = fmt_gpa(gpa_ky)

            self.table.setItem(row, 0, _item(ky.get("hoc_ky", "—")))
            gpa_item = _item(gpa_str, center=True)
            if gpa_ky is not None:
                gpa_item.setForeground(
                    QColor(SUCCESS) if gpa_ky >= 5.0 else QColor(DANGER)
                )
            self.table.setItem(row, 1, gpa_item)
            self.table.setItem(row, 2, _item(str(tc_ky), center=True))
            self.table.setItem(row, 3, _item(xl_ky))

        if not by_ky:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, _item("Chưa có dữ liệu theo kỳ"))


# ── Helpers nội bộ ────────────────────────────────────────────────────────────

def _item(text: str, center: bool = False):
    from PyQt6.QtWidgets import QTableWidgetItem
    it = QTableWidgetItem(str(text))
    if center:
        it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return it


def _xep_loai_mon(diem: float) -> str:
    if diem >= 9.0:  return "Xuất sắc"
    if diem >= 8.0:  return "Giỏi"
    if diem >= 7.0:  return "Khá"
    if diem >= 5.0:  return "Trung bình"
    if diem >= 4.0:  return "Yếu"
    return "Kém"


def _xep_loai_gpa(gpa) -> str:
    if gpa is None: return "—"
    if gpa >= 8.5:  return "Xuất sắc"
    if gpa >= 7.0:  return "Giỏi"
    if gpa >= 5.5:  return "Khá"
    if gpa >= 4.0:  return "Trung bình"
    return "Yếu"
