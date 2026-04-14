from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLineEdit, QComboBox, QPushButton,
    QLabel, QFrame, QDialog, QGridLayout, QDoubleSpinBox, QMessageBox, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from views.base_view import BaseView, QSS_INPUT
from controllers.grade import GradeController
from controllers.student import StudentController
from models.student import Student
from utils.config import (PRIMARY, SECONDARY, BORDER, TEXT_LIGHT, TEXT_MUTED,
                           ACCENT, HIGHLIGHT, DANGER, SUCCESS, WARNING, HOC_KY_LIST)
from utils.helpers import fmt_gpa, badge_color

COLS = ["Mã HP", "Tên học phần", "TC", "Giữa kỳ", "Cuối kỳ", "Tổng kết", "Xếp loại", "Kết quả"]


class GradeView(BaseView):
    PAGE_TITLE = "Điểm số"
    PAGE_SUB   = "Tra cứu và nhập điểm sinh viên"

    def __init__(self):
        self._ctrl    = GradeController()
        self._sv_ctrl = StudentController()
        self._student: Student | None = None
        super().__init__()

    def build_ui(self):
        # Search row
        sr = QHBoxLayout(); sr.setSpacing(8)
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
        btn_search.setStyleSheet(f"QPushButton{{background:{ACCENT};color:{TEXT_LIGHT};border:none;border-radius:6px;font-size:13px;font-weight:600;padding:0 16px;}}QPushButton:hover{{background:#1a4a80;}}")
        btn_search.clicked.connect(self._search)
        sr.addWidget(self.inp_mssv, stretch=1)
        sr.addWidget(self.cmb_hk)
        sr.addWidget(btn_search)
        self._root.addLayout(sr)

        # Main layout
        main = QHBoxLayout(); main.setSpacing(14)

        # Profile card
        self.profile = self._make_profile_card()
        main.addWidget(self.profile, stretch=0)

        # Right: button + table + summary
        right = QVBoxLayout(); right.setSpacing(10)
        btn_row = QHBoxLayout(); btn_row.addStretch()
        self.btn_nhap = self.make_btn("+ Nhập điểm", "primary")
        self.btn_nhap.clicked.connect(self._open_nhap)
        btn_row.addWidget(self.btn_nhap)
        right.addLayout(btn_row)

        self.table = self.make_table(COLS)
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 40)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 90)
        right.addWidget(self.table)

        self.lbl_summary = QLabel("")
        self.lbl_summary.setStyleSheet(f"background:{SECONDARY};border-radius:6px;padding:8px 14px;font-size:12px;color:{TEXT_MUTED};")
        right.addWidget(self.lbl_summary)
        main.addLayout(right, stretch=1)
        self._root.addLayout(main)

    def _make_profile_card(self) -> QFrame:
        f = QFrame()
        f.setFixedWidth(210)
        f.setStyleSheet(f"QFrame{{background:{SECONDARY};border:1px solid {BORDER};border-radius:10px;}}")
        l = QVBoxLayout(f)
        l.setContentsMargins(16, 20, 16, 20)
        l.setSpacing(6)
        l.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.av = QLabel("?")
        self.av.setFixedSize(52, 52)
        self.av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.av.setStyleSheet(f"background:{ACCENT};color:{TEXT_LIGHT};border-radius:26px;font-size:18px;font-weight:700;border:none;")

        self.p_name = QLabel("—")
        self.p_name.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.p_name.setStyleSheet(f"color:{TEXT_LIGHT};border:none;")
        self.p_name.setWordWrap(True)
        self.p_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.p_lop = QLabel("")
        self.p_lop.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;border:none;")
        self.p_lop.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet(f"color:{BORDER};")

        self.p_vals: dict[str, QLabel] = {}
        l.addWidget(self.av, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.p_name)
        l.addWidget(self.p_lop)
        l.addWidget(sep)

        for key in ["GPA tích lũy", "Xếp loại", "TC tích lũy", "Cảnh báo"]:
            row = QHBoxLayout()
            k = QLabel(key); k.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;border:none;")
            v = QLabel("—"); v.setStyleSheet(f"color:{TEXT_LIGHT};font-size:12px;font-weight:600;border:none;")
            v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.p_vals[key] = v
            row.addWidget(k); row.addStretch(); row.addWidget(v)
            w = QWidget(); w.setLayout(row)
            l.addWidget(w)
        l.addStretch()
        return f

    def _search(self):
        mssv = self.inp_mssv.text().strip()
        if not mssv:
            return
        self._sv_ctrl.load_one(mssv, on_success=self._on_sv, on_error=self._default_error)

    def _on_sv(self, sv: Student):
        self._student = sv
        self.av.setText(sv.avatar_text)
        self.p_name.setText(sv.ho_ten)
        self.p_lop.setText(f"{sv.lop} · {sv.khoa}")
        self._reload()

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
        self.table.setRowCount(len(items))

        for row, d in enumerate(items):
            from models.grade import Grade
            g = Grade.from_dict(d)
            self.table.setItem(row, 0, self.cell(g.ma_hp))
            self.table.setItem(row, 1, self.cell(g.ten_hp, bold=True))
            self.table.setItem(row, 2, self.cell(str(g.so_tin_chi), align=Qt.AlignmentFlag.AlignCenter))
            self.table.setItem(row, 3, self.cell(g.diem_gk_display, align=Qt.AlignmentFlag.AlignCenter))
            self.table.setItem(row, 4, self.cell(g.diem_ck_display, align=Qt.AlignmentFlag.AlignCenter))
            tong_item = self.cell(g.tong_ket_display, align=Qt.AlignmentFlag.AlignCenter, bold=True,
                                   color=SUCCESS if g.dat else DANGER)
            self.table.setItem(row, 5, tong_item)
            self.table.setItem(row, 6, self.cell(g.xep_loai if hasattr(g, 'xep_loai') else ""))
            self.table.setItem(row, 7, self.badge_cell(g.ket_qua))

        gpa_tl = data.get("gpa_tich_luy")
        tc_dat = data.get("tin_chi_dat", 0)
        tc_dk  = data.get("tin_chi_dang_ky", 0)
        xl     = data.get("xep_loai", "—")
        cb     = data.get("canh_bao", "")

        from utils.helpers import fmt_gpa, xep_loai
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

    def _open_nhap(self):
        if not self._student:
            QMessageBox.information(self, "Thông báo", "Vui lòng tìm kiếm sinh viên trước.")
            return
        dlg = GradeForm(mssv=self._student.mssv, on_save=self._reload)
        dlg.exec()


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
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        root.addWidget(title)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet(f"color:{BORDER};")
        root.addWidget(sep)

        grid = QGridLayout(); grid.setSpacing(10)

        def lbl(t):
            l = QLabel(t); l.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-weight:600;"); l.setFixedWidth(110); return l

        def spin():
            s = QDoubleSpinBox(); s.setRange(0,10); s.setSingleStep(0.5); s.setDecimals(1)
            s.setFixedHeight(34); s.setStyleSheet(QSS_INPUT); return s

        self.f_mahp  = QLineEdit(); self.f_mahp.setPlaceholderText("VD: CS101"); self.f_mahp.setFixedHeight(34); self.f_mahp.setStyleSheet(QSS_INPUT)
        self.f_hk    = QComboBox(); self.f_hk.addItems(HOC_KY_LIST); self.f_hk.setFixedHeight(34); self.f_hk.setStyleSheet(QSS_INPUT)
        self.f_gk    = spin()
        self.f_ck    = spin()
        self.lbl_tong = QLabel("Tổng kết: —")
        self.lbl_tong.setStyleSheet(f"color:{ACCENT};font-size:13px;font-weight:600;")
        self.f_gk.valueChanged.connect(self._update_tong)
        self.f_ck.valueChanged.connect(self._update_tong)

        for i,(l,w) in enumerate([("Mã HP *",self.f_mahp),("Học kỳ *",self.f_hk),("Điểm GK (40%)",self.f_gk),("Điểm CK (60%)",self.f_ck)]):
            grid.addWidget(lbl(l),i,0); grid.addWidget(w,i,1)
        root.addLayout(grid)
        root.addWidget(self.lbl_tong)
        root.addStretch()

        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Hủy"); bc.setFixedHeight(34); bc.clicked.connect(self.reject)
        bc.setStyleSheet(f"QPushButton{{background:transparent;color:{TEXT_MUTED};border:1px solid {BORDER};border-radius:6px;padding:0 16px;}}QPushButton:hover{{color:{TEXT_LIGHT};}}")
        self.bs = QPushButton("Lưu điểm"); self.bs.setFixedHeight(34); self.bs.clicked.connect(self._save)
        self.bs.setStyleSheet(f"QPushButton{{background:{HIGHLIGHT};color:white;border:none;border-radius:6px;font-weight:700;padding:0 20px;}}QPushButton:hover{{background:#c73050;}}")
        btn_row.addWidget(bc); btn_row.addWidget(self.bs); root.addLayout(btn_row)

    def _update_tong(self):
        from utils.config import TRONG_SO_GK, TRONG_SO_CK
        t = round(self.f_gk.value() * TRONG_SO_GK + self.f_ck.value() * TRONG_SO_CK, 2)
        clr = SUCCESS if t >= 5.0 else DANGER
        self.lbl_tong.setText(f"Tổng kết: {t:.2f}")
        self.lbl_tong.setStyleSheet(f"color:{clr};font-size:13px;font-weight:600;")

    def _save(self):
        self.bs.setEnabled(False)
        def ok(_):
            if self._on_save: self._on_save()
            self.accept()
        def err(msg):
            self.bs.setEnabled(True)
            QMessageBox.warning(self, "Lỗi", msg)
        self._ctrl.create_grade(
            self._mssv, self.f_mahp.text().strip(),
            self.f_hk.currentText(),
            self.f_gk.value(), self.f_ck.value(),
            on_success=ok, on_error=err,
        )