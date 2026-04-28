from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLineEdit, QComboBox,
    QMessageBox, QFileDialog, QWidget, QPushButton,
    QDialog, QGridLayout, QLabel, QDateEdit, QFrame,
    QScrollArea, QCheckBox, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QFont, QColor
from views.base_view import BaseView, QSS_INPUT, QSS_INPUT_LIGHT, QSS_TABLE
from controllers.student import StudentController
from utils.config import (
    PRIMARY, SECONDARY, ACCENT, HIGHLIGHT, TEXT_LIGHT, TEXT_MUTED, BORDER,
    TRANG_THAI_SV, KHOA_LIST, GIOI_TINH, SUCCESS, DANGER, WARNING, INFO,
)
from utils.helpers import fmt_date, badge_color, fmt_gpa

LOAI_GIAY_YEU_CAU = [
    "CCCD/CMND", "Giấy khai sinh", "Học bạ THPT",
    "Bằng tốt nghiệp THPT", "Ảnh thẻ 3x4", "Sổ hộ khẩu",
]

COLS = ["MSSV", "Họ và tên", "Lớp", "Khoa", "Ngày sinh", "Trạng thái", "Thao tác"]


class StudentView(BaseView):
    PAGE_TITLE = "Sinh viên"
    PAGE_SUB   = "Quản lý hồ sơ sinh viên"

    def __init__(self):
        self._ctrl      = StudentController()
        self._khoa_list = list(KHOA_LIST)   # fallback; sẽ được replace bởi API
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

        # ── Toolbar cơ bản ────────────────────────────────────────────────
        tb = QHBoxLayout()
        tb.setSpacing(8)
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm theo MSSV hoặc họ tên...")
        self.inp_search.setFixedHeight(34)
        self.inp_search.setStyleSheet(QSS_INPUT)
        self.inp_search.textChanged.connect(lambda: self._timer.start(400))

        self.cmb_khoa = self._combo(["Tất cả khoa"] + self._khoa_list)
        self.cmb_tt   = self._combo(["Tất cả trạng thái"] + TRANG_THAI_SV)
        self.cmb_khoa.currentIndexChanged.connect(self._load)
        self.cmb_tt.currentIndexChanged.connect(self._load)

        self.inp_lop = QLineEdit()
        self.inp_lop.setPlaceholderText("Lọc theo lớp...")
        self.inp_lop.setFixedHeight(34)
        self.inp_lop.setFixedWidth(120)
        self.inp_lop.setStyleSheet(QSS_INPUT)
        self.inp_lop.textChanged.connect(lambda: self._timer.start(400))

        btn_adv = QPushButton("▼ Lọc nâng cao")
        btn_adv.setFixedHeight(34)
        btn_adv.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_adv.setStyleSheet(
            f"QPushButton{{background:transparent;color:{ACCENT};border:1px solid {ACCENT};"
            f"border-radius:6px;font-size:12px;padding:0 10px;}}"
            f"QPushButton:hover{{background:{ACCENT};color:white;}}"
        )
        btn_adv.clicked.connect(self._toggle_adv)
        self._btn_adv = btn_adv

        tb.addWidget(self.inp_search, stretch=1)
        tb.addWidget(self.inp_lop)
        tb.addWidget(self.cmb_khoa)
        tb.addWidget(self.cmb_tt)
        tb.addWidget(btn_adv)
        self._root.addLayout(tb)

        # ── Bộ lọc nâng cao (ẩn mặc định) ───────────────────────────────
        self._adv_frame = QFrame()
        self._adv_frame.setVisible(False)
        self._adv_frame.setStyleSheet(
            f"QFrame{{background:rgba(37,99,235,0.07);border:1px solid rgba(37,99,235,0.2);"
            f"border-radius:8px;}}"
        )
        adv_lay = QHBoxLayout(self._adv_frame)
        adv_lay.setContentsMargins(14, 8, 14, 8)
        adv_lay.setSpacing(20)

        adv_lay.addWidget(QLabel("Năm nhập học:").also(
            lambda l: l.setStyleSheet(f"color:{TEXT_MUTED};font-size:12px;border:none;")
        ) if False else self._adv_label("Năm nhập học:"))
        self.inp_nam = QLineEdit()
        self.inp_nam.setPlaceholderText("VD: 2022")
        self.inp_nam.setFixedSize(90, 30)
        self.inp_nam.setStyleSheet(QSS_INPUT)
        self.inp_nam.textChanged.connect(lambda: self._timer.start(400))
        adv_lay.addWidget(self.inp_nam)

        self.chk_thieu_gt = QCheckBox("Thiếu giấy tờ")
        self.chk_thieu_gt.setStyleSheet(f"color:{TEXT_LIGHT};font-size:13px;")
        self.chk_thieu_gt.stateChanged.connect(self._load)
        adv_lay.addWidget(self.chk_thieu_gt)

        self.chk_no_hp = QCheckBox("Nợ học phí")
        self.chk_no_hp.setStyleSheet(f"color:{TEXT_LIGHT};font-size:13px;")
        self.chk_no_hp.stateChanged.connect(self._load)
        adv_lay.addWidget(self.chk_no_hp)

        btn_clear_adv = QPushButton("Xóa bộ lọc")
        btn_clear_adv.setFixedHeight(28)
        btn_clear_adv.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear_adv.setStyleSheet(
            f"QPushButton{{background:transparent;color:{TEXT_MUTED};border:1px solid {BORDER};"
            f"border-radius:5px;font-size:11px;padding:0 10px;}}"
            f"QPushButton:hover{{color:{TEXT_LIGHT};}}"
        )
        btn_clear_adv.clicked.connect(self._clear_adv)
        adv_lay.addWidget(btn_clear_adv)
        adv_lay.addStretch()
        self._root.addWidget(self._adv_frame)

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
        self.lbl_count.setStyleSheet("color:#64748B;font-size:13px;font-family:Arial;")
        self._root.addWidget(self.lbl_count)

    def _adv_label(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(f"color:{TEXT_MUTED};font-size:12px;border:none;")
        return l

    def _toggle_adv(self):
        visible = not self._adv_frame.isVisible()
        self._adv_frame.setVisible(visible)
        self._btn_adv.setText("▲ Lọc nâng cao" if visible else "▼ Lọc nâng cao")

    def _clear_adv(self):
        self.inp_nam.clear()
        self.chk_thieu_gt.setChecked(False)
        self.chk_no_hp.setChecked(False)

    def refresh(self):
        self._load_khoa_list()
        self._load()

    def _load_khoa_list(self):
        def _ok(khoa_list: list):
            if not khoa_list:
                return
            self._khoa_list = khoa_list
            current = self.cmb_khoa.currentText()
            self.cmb_khoa.blockSignals(True)
            self.cmb_khoa.clear()
            self.cmb_khoa.addItems(["Tất cả khoa"] + khoa_list)
            # Giữ lại lựa chọn cũ nếu vẫn tồn tại
            idx = self.cmb_khoa.findText(current)
            self.cmb_khoa.setCurrentIndex(idx if idx >= 0 else 0)
            self.cmb_khoa.blockSignals(False)

        self._ctrl.load_khoa_list(on_success=_ok, on_error=lambda _: None)

    def _load(self):
        search        = self.inp_search.text().strip()
        khoa          = self.cmb_khoa.currentText() if self.cmb_khoa.currentIndex() > 0 else ""
        tt            = self.cmb_tt.currentText()   if self.cmb_tt.currentIndex()   > 0 else ""
        lop           = self.inp_lop.text().strip() if hasattr(self, "inp_lop") else ""
        nam_txt       = self.inp_nam.text().strip() if hasattr(self, "inp_nam") else ""
        nam_nhap_hoc  = int(nam_txt) if nam_txt.isdigit() else None
        thieu_giay_to = self.chk_thieu_gt.isChecked() if hasattr(self, "chk_thieu_gt") else False
        no_hoc_phi    = self.chk_no_hp.isChecked()    if hasattr(self, "chk_no_hp")    else False
        self.run_async(
            lambda: self._ctrl._svc.get_list(
                search, khoa, tt, lop,
                nam_nhap_hoc=nam_nhap_hoc,
                thieu_giay_to=thieu_giay_to,
                no_hoc_phi=no_hoc_phi,
            ),
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
                ("Xem",  lambda _, m=mssv: self._open_profile(m), SUCCESS),
                ("Sửa",  lambda _, m=mssv: self._open_edit(m),    ACCENT),
                ("Xóa",  lambda _, m=mssv: self._delete(m),       DANGER),
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

    def _open_profile(self, mssv: str):
        try:
            raw = self._ctrl._svc.get_by_mssv(mssv)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))
            return
        dlg = StudentProfileDialog(data=raw)
        dlg.exec()

    def _open_add(self):
        def _after_save():
            self._load_khoa_list()
            self._load()
            _show_required_docs_notice(self)

        dlg = StudentForm(on_save=_after_save, khoa_list=self._khoa_list)
        dlg.exec()

    def _open_edit(self, mssv: str):
        raw = self._ctrl._svc.get_by_mssv(mssv)
        dlg = StudentForm(data=raw, on_save=self._load, khoa_list=self._khoa_list)
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
    def __init__(self, data: dict | None = None, on_save=None, khoa_list: list | None = None):
        super().__init__()
        self._data      = data or {}
        self._on_save   = on_save
        self._ctrl      = StudentController()
        self._is_edit   = bool(data)
        self._khoa_list = khoa_list or list(KHOA_LIST)
        self.setWindowTitle("Sửa sinh viên" if self._is_edit else "Thêm sinh viên")
        self.setFixedSize(520, 780)
        self.setStyleSheet("background:#FFFFFF; color:#1E293B; font-family:Arial;")
        self._build()
        if data:
            self._fill(data)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)

        title = QLabel(self.windowTitle())
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color:#0F172A;")
        root.addWidget(title)

        sep = QFrame(); sep.setFixedHeight(2)
        sep.setStyleSheet("background:#E2E8F0; border:none;")
        root.addWidget(sep)

        grid = QGridLayout()
        grid.setSpacing(10)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet("color:#475569;font-size:13px;font-weight:600;font-family:Arial;")
            l.setFixedWidth(130)
            return l

        def inp(ph=""):
            i = QLineEdit()
            i.setPlaceholderText(ph)
            i.setFixedHeight(36)
            i.setStyleSheet(QSS_INPUT_LIGHT)
            return i

        def cmb(items):
            c = QComboBox()
            c.addItems(items)
            c.setFixedHeight(36)
            c.setStyleSheet(QSS_INPUT_LIGHT)
            return c

        self.f_mssv      = inp("VD: SV001")
        self.f_hoten     = inp("Nguyễn Văn A")
        self.f_email     = inp("sv@abc.edu.vn")
        self.f_sdt       = inp("0901234567")
        self.f_lop       = inp("CNTT-K67")
        self.f_diachi    = inp("Số nhà, đường, phường/xã, tỉnh/thành")
        self.f_ns        = QDateEdit()
        self.f_ns.setCalendarPopup(True)
        self.f_ns.setDate(QDate(2003, 1, 1))
        self.f_ns.setFixedHeight(34)
        self.f_ns.setStyleSheet(QSS_INPUT_LIGHT)
        self.f_gt        = cmb(GIOI_TINH)
        self.f_khoa      = cmb(self._khoa_list)
        self.f_tt        = cmb(TRANG_THAI_SV)
        self.f_nam_nhap  = inp("VD: 2022")
        self.f_doi_tuong = inp("VD: Hộ nghèo, Dân tộc thiểu số...")
        self.f_cha       = inp("Họ tên cha")
        self.f_me        = inp("Họ tên mẹ")
        self.f_sdt_ph    = inp("Số điện thoại phụ huynh")

        rows = [
            ("Mã sinh viên *", self.f_mssv),
            ("Họ và tên *",    self.f_hoten),
            ("Ngày sinh",      self.f_ns),
            ("Giới tính",      self.f_gt),
            ("Email",          self.f_email),
            ("Số điện thoại",  self.f_sdt),
            ("Khoa *",         self.f_khoa),
            ("Lớp *",          self.f_lop),
            ("Nơi ở hiện tại", self.f_diachi),
            ("Năm nhập học",   self.f_nam_nhap),
            ("Đối tượng ưu tiên", self.f_doi_tuong),
            ("Họ tên cha",     self.f_cha),
            ("Họ tên mẹ",      self.f_me),
            ("SĐT phụ huynh",  self.f_sdt_ph),
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
        btn_cancel.setStyleSheet("""
            QPushButton {
                background:#F8FAFC; color:#64748B;
                border:1.5px solid #E2E8F0; border-radius:9px;
                font-size:13px; font-family:Arial; padding:0 18px;
            }
            QPushButton:hover { background:#F1F5F9; color:#1E293B; }
        """)
        btn_cancel.clicked.connect(self.reject)
        self.btn_save = QPushButton("Lưu")
        self.btn_save.setFixedHeight(38)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #2563EB, stop:1 #7C3AED);
                color:white; border:none; border-radius:9px;
                font-size:13px; font-weight:700; font-family:Arial; padding:0 24px;
            }
            QPushButton:hover { background:#1D4ED8; }
            QPushButton:disabled { background:#CBD5E1; color:#94A3B8; }
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
        self.f_sdt.setText(d.get("so_dien_thoai", ""))
        self.f_lop.setText(d.get("lop", ""))
        self.f_diachi.setText(d.get("dia_chi", ""))
        self.f_nam_nhap.setText(str(d.get("nam_nhap_hoc", "") or ""))
        self.f_doi_tuong.setText(d.get("doi_tuong", "") or "")
        self.f_cha.setText(d.get("ho_ten_cha", "") or "")
        self.f_me.setText(d.get("ho_ten_me", "") or "")
        self.f_sdt_ph.setText(d.get("sdt_phu_huynh", "") or "")
        ns = d.get("ngay_sinh", "")
        if ns:
            self.f_ns.setDate(QDate.fromString(ns[:10], "yyyy-MM-dd"))
        for cmb, key in [(self.f_gt, "gioi_tinh"), (self.f_khoa, "khoa"), (self.f_tt, "trang_thai")]:
            idx = cmb.findText(d.get(key, ""))
            if idx >= 0:
                cmb.setCurrentIndex(idx)

    def _collect(self) -> dict:
        nam = self.f_nam_nhap.text().strip()
        return {
            "mssv":           self.f_mssv.text().strip(),
            "ho_ten":         self.f_hoten.text().strip(),
            "ngay_sinh":      self.f_ns.date().toString("yyyy-MM-dd"),
            "gioi_tinh":      self.f_gt.currentText(),
            "email":          self.f_email.text().strip(),
            "so_dien_thoai":  self.f_sdt.text().strip(),
            "khoa":           self.f_khoa.currentText(),
            "lop":            self.f_lop.text().strip(),
            "dia_chi":        self.f_diachi.text().strip(),
            "trang_thai":     self.f_tt.currentText(),
            "nam_nhap_hoc":   int(nam) if nam.isdigit() else None,
            "doi_tuong":      self.f_doi_tuong.text().strip() or None,
            "ho_ten_cha":     self.f_cha.text().strip() or None,
            "ho_ten_me":      self.f_me.text().strip() or None,
            "sdt_phu_huynh":  self.f_sdt_ph.text().strip() or None,
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


def _show_required_docs_notice(parent):
    """Show popup listing all required documents after adding a new student."""
    msg = QMessageBox(parent)
    msg.setWindowTitle("Thông báo hồ sơ nhập học")
    msg.setIcon(QMessageBox.Icon.Information)
    docs_list = "\n".join(f"  • {d}" for d in LOAI_GIAY_YEU_CAU)
    msg.setText(
        "Sinh viên mới đã được thêm thành công!\n\n"
        "Yêu cầu nộp các giấy tờ hồ sơ sau:\n\n"
        f"{docs_list}\n\n"
        "Vui lòng cập nhật tình trạng nộp hồ sơ trong mục Giấy tờ."
    )
    msg.exec()


# ══════════════════════════════════════════════════════════════════════════════
# Dialog: Hồ sơ sinh viên đầy đủ — 4 tabs
# ══════════════════════════════════════════════════════════════════════════════
class StudentProfileDialog(QDialog):
    """Hiển thị đầy đủ hồ sơ sinh viên với 4 tabs tích hợp."""

    def __init__(self, data: dict):
        super().__init__()
        self._data = data
        mssv   = data.get("mssv", "")
        ho_ten = data.get("ho_ten", "Sinh viên")
        self.setWindowTitle(f"Hồ sơ sinh viên — {ho_ten}")
        self.setMinimumSize(820, 640)
        self.setStyleSheet("background:#FFFFFF; color:#1E293B; font-family:Arial;")

        # Load all data synchronously (dialog is modal)
        from controllers.document import DocumentService
        from controllers.grade import GradeService
        from controllers.tuition import TuitionService

        try:
            self._docs = DocumentService().get_docs(mssv) or []
        except Exception:
            self._docs = []
        try:
            self._transcript = GradeService().get_transcript(mssv, "")
        except Exception:
            self._transcript = {}
        try:
            raw_tuition = TuitionService().get_list(search=mssv)
            items = raw_tuition if isinstance(raw_tuition, list) else raw_tuition.get("items", [])
            self._tuition = next((t for t in items if t.get("mssv") == mssv), None)
        except Exception:
            self._tuition = None

        self._build(data)

    def _build(self, d: dict):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────
        header = QFrame()
        header.setStyleSheet("QFrame{background:#F8FAFC;border-bottom:1.5px solid #E2E8F0;}")
        header.setFixedHeight(110)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 14, 24, 14)
        hl.setSpacing(16)

        from models.student import Student as _Sv
        sv_tmp = _Sv(mssv=d.get("mssv", "?"), ho_ten=d.get("ho_ten", "?"))
        av = QLabel(sv_tmp.avatar_text)
        av.setFixedSize(64, 64)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(
            "background:#DBEAFE;color:#2563EB;border-radius:32px;"
            "font-size:20px;font-weight:700;font-family:Arial;border:none;"
        )
        info_col = QVBoxLayout()
        info_col.setSpacing(3)
        name_lbl = QLabel(d.get("ho_ten", "—"))
        name_lbl.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        name_lbl.setStyleSheet("color:#0F172A;border:none;")
        mssv_lbl = QLabel(f"MSSV: {d.get('mssv', '')}  ·  {d.get('lop', '')}  ·  {d.get('khoa', '')}")
        mssv_lbl.setStyleSheet("color:#64748B;font-size:12px;font-family:Arial;border:none;")
        tt = d.get("trang_thai", "")
        tt_clr = {"Đang học": SUCCESS, "Thôi học": DANGER, "Bảo lưu": WARNING}.get(tt, TEXT_MUTED)
        tt_lbl = QLabel(f"● {tt}")
        tt_lbl.setStyleSheet(f"color:{tt_clr};font-size:12px;font-weight:600;border:none;")
        info_col.addWidget(name_lbl)
        info_col.addWidget(mssv_lbl)
        info_col.addWidget(tt_lbl)
        info_col.addStretch()
        hl.addWidget(av)
        hl.addLayout(info_col, stretch=1)

        # Nút chỉnh sửa trong header
        btn_edit_hdr = QPushButton("✏ Chỉnh sửa")
        btn_edit_hdr.setFixedHeight(34)
        btn_edit_hdr.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit_hdr.setStyleSheet(
            f"QPushButton{{background:transparent;color:{ACCENT};border:1px solid {ACCENT};"
            f"border-radius:7px;font-size:12px;padding:0 14px;}}"
            f"QPushButton:hover{{background:{ACCENT};color:white;}}"
        )
        btn_edit_hdr.clicked.connect(lambda: self._open_edit(d))
        hl.addWidget(btn_edit_hdr)
        root.addWidget(header)

        # ── Tab widget ────────────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #FFFFFF; }
            QTabBar::tab {
                background: #F1F5F9; color: #475569; border: none;
                padding: 10px 20px; font-size: 13px; font-family: Arial;
                border-bottom: 3px solid transparent;
            }
            QTabBar::tab:selected {
                background: #FFFFFF; color: #2563EB; font-weight: 700;
                border-bottom: 3px solid #2563EB;
            }
            QTabBar::tab:hover { background: #E2E8F0; }
        """)
        tabs.addTab(self._build_tab_info(d),    "👤  Thông tin")
        tabs.addTab(self._build_tab_grades(),    "📊  Bảng điểm")
        tabs.addTab(self._build_tab_tuition(),   "💰  Học phí")
        tabs.addTab(self._build_tab_docs(),      "📄  Giấy tờ")
        root.addWidget(tabs, stretch=1)

        # ── Footer ────────────────────────────────────────────────────────
        footer = QFrame()
        footer.setStyleSheet("QFrame{background:#F8FAFC;border-top:1.5px solid #E2E8F0;}")
        footer.setFixedHeight(58)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(24, 0, 24, 0)
        fl.setSpacing(10)

        btn_export = QPushButton("⬇ Xuất hồ sơ Excel")
        btn_export.setFixedHeight(36)
        btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export.setStyleSheet(
            f"QPushButton{{background:{SUCCESS};color:white;border:none;border-radius:8px;"
            f"font-size:13px;font-weight:600;padding:0 18px;}}"
            f"QPushButton:hover{{background:#15803D;}}"
        )
        btn_export.clicked.connect(self._export_profile)
        fl.addWidget(btn_export)
        fl.addStretch()

        btn_close = QPushButton("Đóng")
        btn_close.setFixedHeight(36)
        btn_close.setFixedWidth(100)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton{background:#F1F5F9;color:#64748B;border:1.5px solid #E2E8F0;
            border-radius:8px;font-size:13px;font-family:Arial;}
            QPushButton:hover{background:#E2E8F0;color:#1E293B;}
        """)
        btn_close.clicked.connect(self.accept)
        fl.addWidget(btn_close)
        root.addWidget(footer)

    # ── Tab 1: Thông tin cơ bản ───────────────────────────────────────────
    def _build_tab_info(self, d: dict) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:#FFFFFF;border:none;}")
        body = QWidget(); body.setStyleSheet("background:#FFFFFF;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(24, 18, 24, 18)
        bl.setSpacing(0)

        # Missing docs alert
        missing = [doc for doc in self._docs if not doc.da_nop]
        if missing:
            alert = QFrame()
            alert.setStyleSheet("QFrame{background:#FEF2F2;border:1px solid #FECACA;border-radius:8px;margin-bottom:8px;}")
            al = QHBoxLayout(alert); al.setContentsMargins(14, 10, 14, 10)
            al.addWidget(QLabel(f"⚠  Còn thiếu {len(missing)} giấy tờ: {', '.join(doc.loai_giay for doc in missing)}").also(
                lambda lb: lb.setStyleSheet("color:#DC2626;font-size:12px;font-weight:600;border:none;font-family:Arial;")
            ) if False else self._warn_lbl(missing))
            bl.addWidget(alert)

        self._section(bl, "Thông tin cơ bản")
        for label, value in [
            ("Mã sinh viên",      d.get("mssv", "—")),
            ("Họ và tên",         d.get("ho_ten", "—")),
            ("Ngày sinh",         fmt_date(d.get("ngay_sinh", ""))),
            ("Giới tính",         d.get("gioi_tinh", "—")),
            ("Khoa",              d.get("khoa", "—")),
            ("Lớp",               d.get("lop", "—")),
            ("Năm nhập học",      str(d.get("nam_nhap_hoc", "") or "—")),
            ("Đối tượng ưu tiên", d.get("doi_tuong", "") or "—"),
        ]:
            self._info_row(bl, label, value)

        self._sep(bl)
        self._section(bl, "Liên lạc & Cư trú")
        for label, value in [
            ("Số điện thoại",  d.get("so_dien_thoai", "—")),
            ("Email",          d.get("email", "—")),
            ("Nơi ở hiện tại", d.get("dia_chi", "") or "—"),
        ]:
            self._info_row(bl, label, value)

        self._sep(bl)
        self._section(bl, "Thông tin gia đình")
        for label, value in [
            ("Họ tên cha",    d.get("ho_ten_cha", "") or "—"),
            ("Họ tên mẹ",     d.get("ho_ten_me", "") or "—"),
            ("SĐT phụ huynh", d.get("sdt_phu_huynh", "") or "—"),
        ]:
            self._info_row(bl, label, value)

        bl.addStretch()
        scroll.setWidget(body)
        return scroll

    # ── Tab 2: Bảng điểm ─────────────────────────────────────────────────
    def _build_tab_grades(self) -> QWidget:
        w = QWidget(); w.setStyleSheet("background:#FFFFFF;")
        lay = QVBoxLayout(w); lay.setContentsMargins(16, 12, 16, 12); lay.setSpacing(10)

        # Summary bar
        summary_frame = QFrame()
        summary_frame.setStyleSheet(
            f"QFrame{{background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;}}"
        )
        sf = QHBoxLayout(summary_frame); sf.setContentsMargins(16, 10, 16, 10); sf.setSpacing(30)
        items_data = self._transcript
        gpa  = items_data.get("gpa_tich_luy")
        xl   = items_data.get("xep_loai", "—")
        tc   = items_data.get("tin_chi_dat", 0)
        cb   = items_data.get("canh_bao", "")

        for lbl_txt, val_txt, clr in [
            ("GPA tích lũy", fmt_gpa(gpa), ACCENT if gpa and gpa >= 5 else DANGER),
            ("Xếp loại",     xl,            SUCCESS),
            ("TC tích lũy",  str(tc),       "#6366F1"),
        ]:
            col = QVBoxLayout(); col.setSpacing(2)
            lv = QLabel(lbl_txt); lv.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;border:none;")
            vv = QLabel(val_txt); vv.setFont(QFont("Arial", 15, QFont.Weight.Bold))
            vv.setStyleSheet(f"color:{clr};border:none;")
            col.addWidget(lv); col.addWidget(vv)
            sf.addLayout(col)
        if cb:
            cb_lbl = QLabel(f"⚠ {cb}")
            cb_lbl.setStyleSheet(f"color:{DANGER};font-size:12px;font-weight:600;border:none;background:rgba(239,68,68,0.1);border-radius:6px;padding:4px 10px;")
            sf.addWidget(cb_lbl)
        sf.addStretch()
        lay.addWidget(summary_frame)

        # Bảng điểm
        grade_cols = ["Mã HP", "Tên học phần", "TC", "Giữa kỳ", "Cuối kỳ", "Tổng kết", "Xếp loại", "Kết quả"]
        tbl = QTableWidget()
        tbl.setColumnCount(len(grade_cols))
        tbl.setHorizontalHeaderLabels(grade_cols)
        tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tbl.verticalHeader().setVisible(False)
        tbl.horizontalHeader().setStretchLastSection(False)
        tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tbl.setAlternatingRowColors(True)
        tbl.setStyleSheet(QSS_TABLE)
        tbl.verticalHeader().setDefaultSectionSize(36)
        for i, w_col in enumerate([80, 0, 36, 76, 76, 76, 80, 72]):
            if w_col: tbl.setColumnWidth(i, w_col)

        from models.grade import Grade as GradeModel
        diem_list = self._transcript.get("diem_list", [])
        tbl.setRowCount(len(diem_list))
        for row, d in enumerate(diem_list):
            g = GradeModel.from_dict(d)
            tbl.setItem(row, 0, _tbl_item(g.ma_hp))
            tbl.setItem(row, 1, _tbl_item(g.ten_hp, bold=True))
            tbl.setItem(row, 2, _tbl_item(str(g.so_tin_chi), center=True))
            tbl.setItem(row, 3, _tbl_item(g.diem_gk_display, center=True))
            tbl.setItem(row, 4, _tbl_item(g.diem_ck_display, center=True))
            it = _tbl_item(g.tong_ket_display, center=True, bold=True)
            it.setForeground(QColor(SUCCESS if g.dat else DANGER))
            tbl.setItem(row, 5, it)
            tbl.setItem(row, 6, _tbl_item(_xep_loai_mon(g.tong_ket), center=True))
            tbl.setItem(row, 7, _tbl_item(g.ket_qua, center=True))
        if not diem_list:
            tbl.setRowCount(1)
            tbl.setItem(0, 0, _tbl_item("Chưa có dữ liệu điểm"))
        lay.addWidget(tbl)

        # Nhập điểm button
        from controllers.grade import GradeController as GC
        mssv = self._data.get("mssv", "")
        btn_nhap = QPushButton("+ Nhập điểm mới")
        btn_nhap.setFixedHeight(34)
        btn_nhap.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_nhap.setStyleSheet(
            f"QPushButton{{background:{ACCENT};color:white;border:none;border-radius:7px;"
            f"font-size:13px;font-weight:600;padding:0 18px;}}"
            f"QPushButton:hover{{background:#1D4ED8;}}"
        )
        def _open_grade_form():
            from views.grade_view import GradeForm
            def _reload():
                try:
                    self._transcript = GC()._svc.get_transcript(mssv, "")
                except Exception:
                    pass
                # Rebuild tab — simple approach: close and reopen not ideal, just refresh table
                diem_list2 = self._transcript.get("diem_list", [])
                from models.grade import Grade as GM2
                tbl.setRowCount(len(diem_list2))
                for r2, d2 in enumerate(diem_list2):
                    g2 = GM2.from_dict(d2)
                    tbl.setItem(r2, 0, _tbl_item(g2.ma_hp))
                    tbl.setItem(r2, 1, _tbl_item(g2.ten_hp, bold=True))
                    tbl.setItem(r2, 2, _tbl_item(str(g2.so_tin_chi), center=True))
                    tbl.setItem(r2, 3, _tbl_item(g2.diem_gk_display, center=True))
                    tbl.setItem(r2, 4, _tbl_item(g2.diem_ck_display, center=True))
                    tbl.setItem(r2, 5, _tbl_item(g2.tong_ket_display, center=True))
                    tbl.setItem(r2, 6, _tbl_item(_xep_loai_mon(g2.tong_ket), center=True))
                    tbl.setItem(r2, 7, _tbl_item(g2.ket_qua, center=True))
            GradeForm(mssv=mssv, on_save=_reload).exec()
        btn_nhap.clicked.connect(_open_grade_form)
        btn_row = QHBoxLayout(); btn_row.addStretch(); btn_row.addWidget(btn_nhap)
        lay.addLayout(btn_row)
        return w

    # ── Tab 3: Học phí ────────────────────────────────────────────────────
    def _build_tab_tuition(self) -> QWidget:
        w = QWidget(); w.setStyleSheet("background:#FFFFFF;")
        lay = QVBoxLayout(w); lay.setContentsMargins(24, 20, 24, 20); lay.setSpacing(14)

        if not self._tuition:
            msg = QLabel("Chưa có thông tin học phí.")
            msg.setStyleSheet(f"color:{TEXT_MUTED};font-size:13px;font-family:Arial;")
            lay.addWidget(msg); lay.addStretch(); return w

        t = self._tuition
        phai_nop  = t.get("phai_nop", 0) or 0
        mien_giam = t.get("mien_giam", 0) or 0
        da_nop    = t.get("da_nop", 0) or 0
        actual    = max(0, phai_nop - mien_giam)
        con_thieu = max(0, actual - da_nop)
        trang_thai= t.get("trang_thai", "")
        han_nop   = t.get("han_nop", "")

        tt_clr = {
            "Đã nộp": SUCCESS, "Nộp thiếu": WARNING,
            "Chưa nộp": DANGER, "Quá hạn": DANGER,
        }.get(trang_thai, TEXT_MUTED)

        # Status badge
        status_frame = QFrame()
        status_frame.setStyleSheet(
            f"QFrame{{background:{tt_clr}22;border:1.5px solid {tt_clr}55;border-radius:10px;}}"
        )
        sf = QHBoxLayout(status_frame); sf.setContentsMargins(20, 14, 20, 14)
        st_lbl = QLabel(f"Trạng thái: {trang_thai}")
        st_lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        st_lbl.setStyleSheet(f"color:{tt_clr};border:none;")
        sf.addWidget(st_lbl); sf.addStretch()
        if han_nop:
            hn_lbl = QLabel(f"Hạn nộp: {han_nop}")
            hn_lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:13px;border:none;")
            sf.addWidget(hn_lbl)
        lay.addWidget(status_frame)

        # Các dòng số tiền
        def _money_row(label, amount, color):
            f = QFrame()
            f.setStyleSheet(f"QFrame{{background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;}}")
            fl = QHBoxLayout(f); fl.setContentsMargins(18, 12, 18, 12)
            lbl = QLabel(label); lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:13px;font-weight:600;border:none;")
            val = QLabel(f"{int(amount):,} ₫")
            val.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            val.setStyleSheet(f"color:{color};border:none;")
            fl.addWidget(lbl); fl.addStretch(); fl.addWidget(val)
            lay.addWidget(f)

        _money_row("Phải nộp (sau miễn giảm)", actual, "#2563EB")
        _money_row("Đã nộp", da_nop, SUCCESS)
        _money_row("Còn thiếu", con_thieu, DANGER if con_thieu > 0 else SUCCESS)

        if mien_giam > 0:
            note = QLabel(f"Miễn giảm: {int(mien_giam):,} ₫  —  {t.get('ly_do_mien_giam') or 'Không ghi lý do'}")
            note.setStyleSheet(f"color:{TEXT_MUTED};font-size:12px;font-family:Arial;border:none;")
            lay.addWidget(note)
        lay.addStretch()
        return w

    # ── Tab 4: Giấy tờ ────────────────────────────────────────────────────
    def _build_tab_docs(self) -> QWidget:
        w = QWidget(); w.setStyleSheet("background:#FFFFFF;")
        lay = QVBoxLayout(w); lay.setContentsMargins(16, 12, 16, 12); lay.setSpacing(8)

        # Summary
        total  = len(self._docs)
        da_nop = sum(1 for d in self._docs if d.da_nop)
        clr    = SUCCESS if da_nop == total else DANGER
        sum_lbl = QLabel(f"Đã nộp: {da_nop}/{total} giấy tờ")
        sum_lbl.setStyleSheet(f"color:{clr};font-size:13px;font-weight:700;font-family:Arial;border:none;")
        lay.addWidget(sum_lbl)

        if not self._docs:
            lay.addWidget(QLabel("Chưa có thông tin giấy tờ").also(  # dummy
                lambda l: l.setStyleSheet(f"color:{TEXT_MUTED};font-size:13px;")
            ) if False else self._no_data_lbl("Chưa có thông tin giấy tờ"))
            lay.addStretch(); return w

        doc_cols = ["Loại giấy tờ", "Trạng thái", "Ngày nộp", "File đính kèm", "Ghi chú"]
        tbl = QTableWidget()
        tbl.setColumnCount(len(doc_cols))
        tbl.setHorizontalHeaderLabels(doc_cols)
        tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tbl.verticalHeader().setVisible(False)
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        tbl.setAlternatingRowColors(True)
        tbl.setStyleSheet("""
            QTableWidget{background:#FFFFFF;border:none;color:#1E293B;font-size:13px;font-family:Arial;gridline-color:#F1F5F9;}
            QTableWidget::item{padding:6px 10px;}QTableWidget::item:selected{background:#DBEAFE;color:#1E3A8A;}
            QTableWidget::item:alternate{background:#F8FAFC;}
            QHeaderView::section{background:#F1F5F9;color:#475569;font-size:11px;font-weight:700;padding:8px 10px;border:none;border-bottom:2px solid #E2E8F0;}
        """)
        tbl.setColumnWidth(1, 100); tbl.setColumnWidth(2, 100); tbl.setColumnWidth(3, 160); tbl.setColumnWidth(4, 150)
        tbl.verticalHeader().setDefaultSectionSize(38)
        tbl.setRowCount(len(self._docs))
        for r, doc in enumerate(self._docs):
            tbl.setItem(r, 0, _tbl_item(doc.loai_giay))
            tt_it = _tbl_item("✓ Đã nộp" if doc.da_nop else "✗ Chưa nộp", center=True, bold=True)
            tt_it.setForeground(QColor(SUCCESS if doc.da_nop else DANGER))
            tbl.setItem(r, 1, tt_it)
            tbl.setItem(r, 2, _tbl_item(fmt_date(doc.ngay_nop) if doc.ngay_nop else "—", center=True))
            tbl.setItem(r, 3, _tbl_item(doc.file_name if doc.has_file else "Chưa có file"))
            tbl.setItem(r, 4, _tbl_item(doc.ghi_chu or ""))
        lay.addWidget(tbl)
        return w

    # ── Actions ───────────────────────────────────────────────────────────
    def _open_edit(self, d: dict):
        ctrl = StudentController()
        dlg = StudentForm(
            data=d, on_save=lambda: None,
            khoa_list=list(KHOA_LIST),
        )
        dlg.exec()

    def _export_profile(self):
        mssv = self._data.get("mssv", "")
        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu hồ sơ Excel", f"hoso_{mssv}.xlsx", "Excel (*.xlsx)"
        )
        if not path:
            return
        from controllers.base import APIClient
        try:
            data = APIClient().get_bytes(f"/sinhvien/{mssv}/export")
            with open(path, "wb") as f:
                f.write(data)
            QMessageBox.information(self, "Thành công", f"Đã xuất hồ sơ:\n{path}")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi xuất hồ sơ", str(e))

    # ── Helpers ───────────────────────────────────────────────────────────
    def _warn_lbl(self, missing) -> QLabel:
        l = QLabel(f"⚠  Còn thiếu {len(missing)} giấy tờ: {', '.join(d.loai_giay for d in missing)}")
        l.setStyleSheet("color:#DC2626;font-size:12px;font-weight:600;border:none;font-family:Arial;")
        l.setWordWrap(True)
        return l

    def _no_data_lbl(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(f"color:{TEXT_MUTED};font-size:13px;font-family:Arial;border:none;")
        return l

    # ── Helpers layout ────────────────────────────────────────────────────
    def _sep(self, layout: QVBoxLayout):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{BORDER};margin:10px 0;")
        layout.addWidget(sep)

    def _section(self, layout: QVBoxLayout, title: str):
        lbl = QLabel(title.upper())
        lbl.setStyleSheet(
            "color:#2563EB;font-size:11px;font-weight:700;"
            "font-family:Arial;letter-spacing:1px;border:none;margin-bottom:4px;"
        )
        layout.addWidget(lbl)

    def _info_row(self, layout: QVBoxLayout, label: str, value: str):
        row = QHBoxLayout()
        row.setSpacing(12)
        lbl = QLabel(label)
        lbl.setFixedWidth(145)
        lbl.setStyleSheet("color:#64748B;font-size:13px;font-family:Arial;border:none;")
        val = QLabel(value)
        val.setStyleSheet(
            "color:#1E293B;font-size:13px;font-weight:500;font-family:Arial;border:none;"
        )
        val.setWordWrap(True)
        row.addWidget(lbl)
        row.addWidget(val, stretch=1)
        wrapper = QWidget()
        wrapper.setStyleSheet("background:transparent;")
        wrapper.setLayout(row)
        wrapper.setFixedHeight(28)
        layout.addWidget(wrapper)


# ── Module-level helpers ──────────────────────────────────────────────────────

def _tbl_item(text: str, center: bool = False, bold: bool = False) -> QTableWidgetItem:
    it = QTableWidgetItem(str(text) if text is not None else "")
    if center:
        it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    if bold:
        f = it.font(); f.setBold(True); it.setFont(f)
    return it


def _xep_loai_mon(diem) -> str:
    if diem is None: return "—"
    if diem >= 9.0:  return "Xuất sắc"
    if diem >= 8.0:  return "Giỏi"
    if diem >= 7.0:  return "Khá"
    if diem >= 5.0:  return "Trung bình"
    if diem >= 4.0:  return "Yếu"
    return "Kém"