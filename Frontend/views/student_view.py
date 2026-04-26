from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLineEdit, QComboBox,
    QMessageBox, QFileDialog, QWidget, QPushButton,
    QDialog, QGridLayout, QLabel, QDateEdit, QFrame,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QFont
from views.base_view import BaseView, QSS_INPUT, QSS_INPUT_LIGHT
from controllers.student import StudentController
from utils.config import (
    PRIMARY, SECONDARY, ACCENT, HIGHLIGHT, TEXT_LIGHT, TEXT_MUTED, BORDER,
    TRANG_THAI_SV, KHOA_LIST, GIOI_TINH, SUCCESS, DANGER, WARNING
)
from utils.helpers import fmt_date, badge_color

LOAI_GIAY_YEU_CAU = [
    "CCCD/CMND", "Giấy khai sinh", "Học bạ THPT",
    "Bằng tốt nghiệp THPT", "Ảnh thẻ 3x4", "Sổ hộ khẩu",
]

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

        self.inp_lop = QLineEdit()
        self.inp_lop.setPlaceholderText("Lọc theo lớp...")
        self.inp_lop.setFixedHeight(34)
        self.inp_lop.setFixedWidth(130)
        self.inp_lop.setStyleSheet(QSS_INPUT)
        self.inp_lop.textChanged.connect(lambda: self._timer.start(400))

        tb.addWidget(self.inp_search, stretch=1)
        tb.addWidget(self.inp_lop)
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
        self.lbl_count.setStyleSheet("color:#64748B;font-size:13px;font-family:Arial;")
        self._root.addWidget(self.lbl_count)

    def refresh(self):
        self._load()

    def _load(self):
        search = self.inp_search.text().strip()
        khoa   = self.cmb_khoa.currentText() if self.cmb_khoa.currentIndex() > 0 else ""
        tt     = self.cmb_tt.currentText()   if self.cmb_tt.currentIndex()   > 0 else ""
        lop    = self.inp_lop.text().strip() if hasattr(self, "inp_lop") else ""
        self.run_async(
            lambda: self._ctrl._svc.get_list(search, khoa, tt, lop),
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
            self._load()
            _show_required_docs_notice(self)

        dlg = StudentForm(on_save=_after_save)
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
        self.f_khoa      = cmb(KHOA_LIST)
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
# Dialog: Thông tin cá nhân sinh viên
# ══════════════════════════════════════════════════════════════════════════════
class StudentProfileDialog(QDialog):
    """Hiển thị toàn bộ hồ sơ cá nhân của sinh viên (chỉ đọc)."""

    def __init__(self, data: dict):
        super().__init__()
        self._data = data
        ho_ten = data.get("ho_ten", "Sinh viên")
        self.setWindowTitle(f"Hồ sơ sinh viên — {ho_ten}")
        self.setFixedSize(540, 740)
        self.setStyleSheet("background:#FFFFFF; color:#1E293B; font-family:Arial;")

        # Fetch documents synchronously
        from controllers.document import DocumentService
        try:
            self._docs = DocumentService().get_docs(data.get("mssv", "")) or []
        except Exception:
            self._docs = []

        self._build(data)

    def _build(self, d: dict):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header với avatar ─────────────────────────────────────────────
        header = QFrame()
        header.setStyleSheet(
            "QFrame{background:#F8FAFC; border-bottom:1.5px solid #E2E8F0;}"
        )
        header.setFixedHeight(120)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 16, 24, 16)
        hl.setSpacing(16)

        from models.student import Student as _Sv
        sv_tmp = _Sv(mssv=d.get("mssv", "?"), ho_ten=d.get("ho_ten", "?"))
        av = QLabel(sv_tmp.avatar_text)
        av.setFixedSize(68, 68)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(
            "background:#DBEAFE;color:#2563EB;border-radius:34px;"
            "font-size:22px;font-weight:700;font-family:Arial;border:none;"
        )

        info_col = QVBoxLayout()
        info_col.setSpacing(3)
        name_lbl = QLabel(d.get("ho_ten", "—"))
        name_lbl.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        name_lbl.setStyleSheet("color:#0F172A;border:none;")
        mssv_lbl = QLabel(d.get("mssv", ""))
        mssv_lbl.setStyleSheet("color:#64748B;font-size:13px;font-family:Arial;border:none;")
        tt = d.get("trang_thai", "")
        tt_clr = {
            "Đang học": SUCCESS, "Thôi học": DANGER, "Bảo lưu": WARNING,
        }.get(tt, TEXT_MUTED)
        tt_lbl = QLabel(f"● {tt}")
        tt_lbl.setStyleSheet(f"color:{tt_clr};font-size:12px;font-weight:600;border:none;")
        info_col.addWidget(name_lbl)
        info_col.addWidget(mssv_lbl)
        info_col.addWidget(tt_lbl)
        info_col.addStretch()
        hl.addWidget(av)
        hl.addLayout(info_col)
        root.addWidget(header)

        # ── Missing docs banner ────────────────────────────────────────────
        missing = [doc for doc in self._docs if not doc.da_nop]
        if missing:
            banner = QFrame()
            banner.setStyleSheet(
                "QFrame{background:#FEF2F2;border-bottom:1px solid #FECACA;}"
            )
            bl2 = QVBoxLayout(banner)
            bl2.setContentsMargins(24, 10, 24, 10)
            bl2.setSpacing(4)
            warn_title = QLabel(f"⚠  Còn thiếu {len(missing)} giấy tờ chưa nộp")
            warn_title.setStyleSheet(
                "color:#DC2626;font-size:13px;font-weight:700;border:none;font-family:Arial;"
            )
            bl2.addWidget(warn_title)
            names = ", ".join(doc.loai_giay for doc in missing)
            warn_detail = QLabel(names)
            warn_detail.setWordWrap(True)
            warn_detail.setStyleSheet(
                "color:#B91C1C;font-size:12px;border:none;font-family:Arial;"
            )
            bl2.addWidget(warn_detail)
            root.addWidget(banner)

        # ── Scrollable body ────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:#FFFFFF;border:none;}")

        body_widget = QWidget()
        body_widget.setStyleSheet("background:#FFFFFF;")
        bl = QVBoxLayout(body_widget)
        bl.setContentsMargins(24, 18, 24, 18)
        bl.setSpacing(0)

        from utils.helpers import fmt_date

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

        self._sep(bl)
        self._section(bl, "Giấy tờ hồ sơ")
        if self._docs:
            for doc in self._docs:
                da_nop = doc.da_nop
                loai   = doc.loai_giay
                ngay   = fmt_date(doc.ngay_nop) if doc.ngay_nop else ""
                dot    = "✓" if da_nop else "✗"
                clr    = SUCCESS if da_nop else DANGER
                row = QHBoxLayout()
                dot_lbl = QLabel(dot)
                dot_lbl.setFixedWidth(20)
                dot_lbl.setStyleSheet(f"color:{clr};font-size:14px;font-weight:700;border:none;")
                name_lbl = QLabel(loai)
                name_lbl.setStyleSheet(
                    f"color:#1E293B;font-size:13px;font-weight:500;font-family:Arial;border:none;"
                )
                date_lbl = QLabel(f"Nộp: {ngay}" if ngay else ("Chưa nộp" if not da_nop else ""))
                date_lbl.setStyleSheet(
                    f"color:{'#64748B' if da_nop else DANGER};font-size:12px;font-family:Arial;border:none;"
                )
                row.addWidget(dot_lbl)
                row.addWidget(name_lbl, stretch=1)
                row.addWidget(date_lbl)
                w = QWidget()
                w.setStyleSheet("background:transparent;")
                w.setLayout(row)
                w.setFixedHeight(28)
                bl.addWidget(w)
        else:
            no_doc = QLabel("Chưa có thông tin giấy tờ")
            no_doc.setStyleSheet("color:#94A3B8;font-size:13px;font-family:Arial;border:none;")
            bl.addWidget(no_doc)

        bl.addStretch()
        scroll.setWidget(body_widget)
        root.addWidget(scroll, stretch=1)

        # ── Footer: nút Đóng ──────────────────────────────────────────────
        footer = QFrame()
        footer.setStyleSheet(
            "QFrame{background:#F8FAFC; border-top:1.5px solid #E2E8F0;}"
        )
        footer.setFixedHeight(58)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(24, 0, 24, 0)
        fl.addStretch()
        btn_close = QPushButton("Đóng")
        btn_close.setFixedHeight(36)
        btn_close.setFixedWidth(110)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton{background:#F1F5F9;color:#64748B;
            border:1.5px solid #E2E8F0;border-radius:9px;
            font-size:13px;font-family:Arial;}
            QPushButton:hover{background:#E2E8F0;color:#1E293B;}
        """)
        btn_close.clicked.connect(self.accept)
        fl.addWidget(btn_close)
        root.addWidget(footer)

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