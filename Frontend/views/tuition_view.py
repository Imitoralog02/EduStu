from __future__ import annotations
from datetime import datetime
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLineEdit, QComboBox,
    QPushButton, QLabel, QFrame, QDialog, QGridLayout,
    QDoubleSpinBox, QMessageBox, QWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from views.base_view import BaseView, QSS_INPUT
from controllers.tuition import TuitionController
from utils.config import (PRIMARY, SECONDARY, BORDER, TEXT_LIGHT, TEXT_MUTED,
                           ACCENT, HIGHLIGHT, DANGER, SUCCESS, WARNING, TRANG_THAI_HP)
from utils.helpers import fmt_money, badge_color

COLS = ["MSSV", "Họ và tên", "Lớp", "Phải nộp", "Đã nộp", "Còn thiếu", "Hạn nộp", "Trạng thái", ""]


class TuitionView(BaseView):
    PAGE_TITLE = "Học phí"
    PAGE_SUB   = "Theo dõi thanh toán & công nợ học kỳ"

    def __init__(self):
        self._ctrl = TuitionController()
        super().__init__()

    def build_ui(self):
        btn_tt = self.make_btn("+ Ghi nhận thanh toán", "primary")
        btn_tt.clicked.connect(lambda: PaymentForm(on_save=self.refresh).exec())
        self.add_action(btn_tt)

        btn_ky = self.make_btn("🎓 Tạo học kỳ mới", "secondary")
        btn_ky.clicked.connect(lambda: NewSemesterDialog(on_save=self.refresh).exec())
        self.add_action(btn_ky)

        # Stat row — số lượng sinh viên
        stat_row = QHBoxLayout(); stat_row.setSpacing(10)
        stat_defs = [
            ("Tổng sinh viên",  ACCENT,   "tong"),
            ("Đã đóng học phí", SUCCESS,  "da_dong"),
            ("Còn nợ học phí",  DANGER,   "con_no"),
        ]
        self._stat_vals: dict[str, QLabel] = {}
        for lbl_txt, clr, key in stat_defs:
            card = QFrame()
            card.setStyleSheet(f"QFrame{{background:#FFFFFF;border:none;border-top:4px solid {clr};border-radius:16px;}}")
            from PyQt6.QtWidgets import QGraphicsDropShadowEffect as _Sh
            sh = _Sh(card); sh.setBlurRadius(16); sh.setOffset(0, 3); sh.setColor(QColor(0, 0, 0, 22))
            card.setGraphicsEffect(sh)
            cl = QVBoxLayout(card); cl.setContentsMargins(20, 14, 20, 14); cl.setSpacing(4)
            lbl = QLabel(lbl_txt); lbl.setStyleSheet("color:#64748B;font-size:13px;font-family:Arial;border:none;")
            val = QLabel("—"); val.setFont(QFont("Arial", 28, QFont.Weight.Bold))
            val.setStyleSheet(f"color:{clr};border:none;")
            sub = QLabel("sinh viên"); sub.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;border:none;")
            cl.addWidget(lbl); cl.addWidget(val); cl.addWidget(sub)
            self._stat_vals[key] = val
            stat_row.addWidget(card)
        self._root.addLayout(stat_row)

        # Toolbar
        tb = QHBoxLayout(); tb.setSpacing(8)
        self.inp_search = QLineEdit()
        self.inp_search.setPlaceholderText("Tìm theo MSSV hoặc họ tên...")
        self.inp_search.setFixedHeight(34); self.inp_search.setStyleSheet(QSS_INPUT)
        self.inp_search.textChanged.connect(self.refresh)
        self.cmb_tt = QComboBox()
        self.cmb_tt.addItems(["Tất cả"] + TRANG_THAI_HP)
        self.cmb_tt.setFixedHeight(34); self.cmb_tt.setMinimumWidth(140); self.cmb_tt.setStyleSheet(QSS_INPUT)
        self.cmb_tt.currentIndexChanged.connect(self.refresh)
        tb.addWidget(self.inp_search, stretch=1); tb.addWidget(self.cmb_tt)
        self._root.addLayout(tb)

        self.table = self.make_table(COLS)
        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(1, 160)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 115)
        self.table.setColumnWidth(4, 115)
        self.table.setColumnWidth(5, 115)
        self.table.setColumnWidth(6, 95)
        self.table.setColumnWidth(7, 95)
        self._root.addWidget(self.table)

    def refresh(self):
        search = self.inp_search.text().strip() if hasattr(self, "inp_search") else ""
        tt = self.cmb_tt.currentText() if hasattr(self, "cmb_tt") and self.cmb_tt.currentIndex() > 0 else ""
        self._ctrl.load_list(search, tt, on_success=self._render, on_error=self._default_error)
        self._ctrl.load_stats(on_success=self._render_stats, on_error=lambda _: None)

    def _render(self, items):
        self.table.setRowCount(len(items))
        for row, t in enumerate(items):
            self.table.setItem(row, 0, self.cell(t.mssv))
            self.table.setItem(row, 1, self.cell(t.ho_ten, bold=True))
            self.table.setItem(row, 2, self.cell(t.lop or "—"))
            self.table.setItem(row, 3, self.cell(t.phai_nop_display))
            self.table.setItem(row, 4, self.cell(t.da_nop_display))
            ct_item = self.cell(t.con_thieu_display, color=DANGER if t.con_thieu > 0 else None)
            self.table.setItem(row, 5, ct_item)
            self.table.setItem(row, 6, self.cell(t.han_nop_display))
            self.table.setItem(row, 7, self.badge_cell(t.trang_thai))

            # Cột hành động
            w = QWidget(); hl = QHBoxLayout(w); hl.setContentsMargins(4, 2, 4, 2); hl.setSpacing(4)

            # Nút thanh toán
            b = QPushButton("Thanh toán")
            b.setFixedHeight(26); b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"QPushButton{{background:transparent;color:{ACCENT};border:1px solid {ACCENT};border-radius:4px;font-size:11px;padding:0 8px;}}QPushButton:hover{{background:{ACCENT};color:white;}}")
            b.clicked.connect(lambda _, obj=t: PaymentForm(mssv=obj.mssv, ho_ten=obj.ho_ten, lop=obj.lop, khoa=obj.khoa, con_thieu=obj.con_thieu, on_save=self.refresh).exec())

            # Nút nhắc nộp (chỉ hiện khi chưa nộp/thiếu/quá hạn)
            bn = QPushButton("⚠ Nhắc nộp")
            bn.setFixedHeight(26); bn.setCursor(Qt.CursorShape.PointingHandCursor)
            bn.setStyleSheet(f"QPushButton{{background:transparent;color:{WARNING};border:1px solid {WARNING};border-radius:4px;font-size:11px;padding:0 8px;}}QPushButton:hover{{background:{WARNING};color:white;}}")
            bn.setVisible(t.is_warning)
            bn.clicked.connect(lambda _, obj=t: self._show_reminder(obj))

            bh = QPushButton("Lịch sử")
            bh.setFixedHeight(26); bh.setCursor(Qt.CursorShape.PointingHandCursor)
            bh.setStyleSheet(f"QPushButton{{background:transparent;color:{SUCCESS};border:1px solid {SUCCESS};border-radius:4px;font-size:11px;padding:0 8px;}}QPushButton:hover{{background:{SUCCESS};color:white;}}")
            bh.clicked.connect(lambda _, obj=t: PaymentHistoryDialog(mssv=obj.mssv, ho_ten=obj.ho_ten).exec())

            hl.addWidget(b); hl.addWidget(bn); hl.addWidget(bh)
            self.table.setCellWidget(row, 8, w)

    def _render_stats(self, stats: dict):
        self._stat_vals["tong"].setText(str(stats.get("tong", 0)))
        self._stat_vals["da_dong"].setText(str(stats.get("da_dong", 0)))
        self._stat_vals["con_no"].setText(str(stats.get("con_no", 0)))

    def _show_reminder(self, t):
        msg = (
            f"<b>Thông báo nhắc nộp học phí</b><br><br>"
            f"Sinh viên: <b>{t.ho_ten}</b> — MSSV: <b>{t.mssv}</b><br>"
            f"Lớp: {t.lop or '—'}  |  Khoa: {t.khoa or '—'}<br>"
            f"Trạng thái: <span style='color:red;'><b>{t.trang_thai}</b></span><br>"
            f"Số tiền còn thiếu: <b>{t.con_thieu_display}</b><br>"
            f"Hạn nộp: <b>{t.han_nop_display or '—'}</b>"
        )
        box = QMessageBox(self)
        box.setWindowTitle("Nhắc nhở nộp học phí")
        box.setText(msg)
        box.setIcon(QMessageBox.Icon.Warning)
        box.exec()


class NewSemesterDialog(QDialog):
    def __init__(self, on_save=None):
        super().__init__()
        self._on_save = on_save
        self._ctrl = TuitionController()
        self.setWindowTitle("Tạo học kỳ mới")
        self.setFixedSize(420, 240)
        self.setStyleSheet(f"background:{PRIMARY};color:{TEXT_LIGHT};")
        self._build()

    def _build(self):
        from datetime import date, timedelta
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20); root.setSpacing(12)

        title = QLabel("Tạo học kỳ mới")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        root.addWidget(title)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet(f"color:{BORDER};")
        root.addWidget(sep)

        han_nop = (date.today() + timedelta(days=7)).strftime("%d/%m/%Y")
        note = QLabel(f"Hạn nộp sẽ tự động đặt là: <b>{han_nop}</b> (7 ngày kể từ hôm nay)")
        note.setStyleSheet(f"color:{WARNING};font-size:12px;border:none;")
        note.setWordWrap(True)
        root.addWidget(note)

        grid = QGridLayout(); grid.setSpacing(10)
        def lbl(t):
            l = QLabel(t); l.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-weight:600;"); l.setFixedWidth(130); return l

        self.f_tien = QDoubleSpinBox()
        self.f_tien.setRange(0, 100_000_000); self.f_tien.setSingleStep(500_000)
        self.f_tien.setDecimals(0); self.f_tien.setValue(4_500_000)
        self.f_tien.setFixedHeight(34); self.f_tien.setStyleSheet(QSS_INPUT)

        self.f_gc = QLineEdit()
        self.f_gc.setPlaceholderText("VD: Học kỳ 1 năm học 2025-2026")
        self.f_gc.setFixedHeight(34); self.f_gc.setStyleSheet(QSS_INPUT)

        for i, (l, w) in enumerate([("Học phí (₫) *", self.f_tien), ("Ghi chú", self.f_gc)]):
            grid.addWidget(lbl(l), i, 0); grid.addWidget(w, i, 1)
        root.addLayout(grid); root.addStretch()

        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Hủy"); bc.setFixedHeight(34); bc.clicked.connect(self.reject)
        bc.setStyleSheet(f"QPushButton{{background:transparent;color:{TEXT_MUTED};border:1px solid {BORDER};border-radius:6px;padding:0 16px;}}QPushButton:hover{{color:{TEXT_LIGHT};}}")
        self.bs = QPushButton("Tạo học kỳ"); self.bs.setFixedHeight(34); self.bs.clicked.connect(self._save)
        self.bs.setStyleSheet(f"QPushButton{{background:{ACCENT};color:white;border:none;border-radius:6px;font-weight:700;padding:0 20px;}}QPushButton:hover{{opacity:0.9;}}")
        btn_row.addWidget(bc); btn_row.addWidget(self.bs)
        root.addLayout(btn_row)

    def _save(self):
        confirm = QMessageBox.question(
            self, "Xác nhận",
            "Tạo học kỳ mới sẽ <b>reset toàn bộ học phí</b> của tất cả sinh viên.<br>Tiếp tục?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self.bs.setEnabled(False)

        def ok(result):
            QMessageBox.information(self, "Thành công",
                f"{result.get('message', 'Đã tạo học kỳ mới')}\n"
                f"Hạn nộp: {result.get('han_nop', '')} (7 ngày)")
            if self._on_save: self._on_save()
            self.accept()

        def err(msg):
            self.bs.setEnabled(True)
            QMessageBox.warning(self, "Lỗi", msg)

        self._ctrl.create_semester(self.f_tien.value(), self.f_gc.text(), on_success=ok, on_error=err)


class PaymentForm(QDialog):
    def __init__(self, mssv: str = "", ho_ten: str = "", lop: str = "", khoa: str = "",
                 con_thieu: float = 0, on_save=None):
        super().__init__()
        self._on_save = on_save
        self._ctrl    = TuitionController()
        self._ho_ten  = ho_ten
        self._lop     = lop
        self._khoa    = khoa
        self.setWindowTitle("Ghi nhận thanh toán học phí")
        self.setFixedSize(400, 310)
        self.setStyleSheet(f"background:{PRIMARY};color:{TEXT_LIGHT};")
        self._build(mssv, con_thieu)

    def _build(self, mssv, con_thieu):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20); root.setSpacing(12)
        title = QLabel("Ghi nhận thanh toán")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold)); root.addWidget(title)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet(f"color:{BORDER};"); root.addWidget(sep)

        grid = QGridLayout(); grid.setSpacing(10)
        def lbl(t):
            l = QLabel(t); l.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-weight:600;"); l.setFixedWidth(120); return l

        self.f_mssv = QLineEdit(mssv); self.f_mssv.setFixedHeight(34); self.f_mssv.setStyleSheet(QSS_INPUT)
        self.f_tien = QDoubleSpinBox()
        self.f_tien.setRange(0, 100_000_000); self.f_tien.setSingleStep(500_000); self.f_tien.setDecimals(0)
        self.f_tien.setValue(max(0, con_thieu)); self.f_tien.setFixedHeight(34); self.f_tien.setStyleSheet(QSS_INPUT)
        self.f_pt = QComboBox()
        self.f_pt.addItems(["Tiền mặt", "Chuyển khoản", "Thẻ ngân hàng", "MoMo"])
        self.f_pt.setFixedHeight(34); self.f_pt.setStyleSheet(QSS_INPUT)
        self.f_gc = QLineEdit(); self.f_gc.setPlaceholderText("Ghi chú..."); self.f_gc.setFixedHeight(34); self.f_gc.setStyleSheet(QSS_INPUT)

        for i, (l, w) in enumerate([("MSSV *", self.f_mssv), ("Số tiền (₫) *", self.f_tien),
                                     ("Phương thức", self.f_pt), ("Ghi chú", self.f_gc)]):
            grid.addWidget(lbl(l), i, 0); grid.addWidget(w, i, 1)
        root.addLayout(grid); root.addStretch()

        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Hủy"); bc.setFixedHeight(34); bc.clicked.connect(self.reject)
        bc.setStyleSheet(f"QPushButton{{background:transparent;color:{TEXT_MUTED};border:1px solid {BORDER};border-radius:6px;padding:0 16px;}}QPushButton:hover{{color:{TEXT_LIGHT};}}")
        self.bs = QPushButton("Xác nhận"); self.bs.setFixedHeight(34); self.bs.clicked.connect(self._save)
        self.bs.setStyleSheet(f"QPushButton{{background:{HIGHLIGHT};color:white;border:none;border-radius:6px;font-weight:700;padding:0 20px;}}QPushButton:hover{{background:#c73050;}}")
        btn_row.addWidget(bc); btn_row.addWidget(self.bs)
        root.addLayout(btn_row)

    def _save(self):
        self.bs.setEnabled(False)

        def ok(result: dict):
            if self._on_save: self._on_save()
            self.accept()
            PaymentBillDialog(
                ho_ten=result.get("ho_ten") or self._ho_ten,
                mssv=result.get("mssv") or self.f_mssv.text().strip(),
                lop=result.get("lop") or self._lop,
                khoa=result.get("khoa") or self._khoa,
                so_tien=result.get("so_tien", self.f_tien.value()),
                phuong_thuc=result.get("phuong_thuc", self.f_pt.currentText()),
                ngay_nop=result.get("ngay_nop", ""),
                trang_thai_moi=result.get("trang_thai_moi", ""),
                con_lai=result.get("con_lai", 0.0),
            ).exec()

        def err(msg):
            self.bs.setEnabled(True)
            QMessageBox.warning(self, "Lỗi", msg)

        self._ctrl.record_payment(
            self.f_mssv.text().strip(), self.f_tien.value(),
            self.f_pt.currentText(), self.f_gc.text(),
            on_success=ok, on_error=err,
        )


class PaymentBillDialog(QDialog):
    """Bill thanh toán hiện sau khi ghi nhận thành công."""

    def __init__(self, ho_ten: str, mssv: str, lop: str, khoa: str,
                 so_tien: float, phuong_thuc: str, ngay_nop: str,
                 trang_thai_moi: str, con_lai: float):
        super().__init__()
        self.setWindowTitle("Biên lai thanh toán học phí")
        self.setFixedSize(440, 380)
        self.setStyleSheet(f"background:{PRIMARY};color:{TEXT_LIGHT};")
        self._build(ho_ten, mssv, lop, khoa, so_tien, phuong_thuc, ngay_nop, trang_thai_moi, con_lai)

    def _build(self, ho_ten, mssv, lop, khoa, so_tien, phuong_thuc, ngay_nop, trang_thai_moi, con_lai):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 20); root.setSpacing(10)

        # Header
        title = QLabel("✅  BIÊN LAI THANH TOÁN HỌC PHÍ")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{SUCCESS};border:none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet(f"color:{BORDER};")
        root.addWidget(sep)

        # Thông tin
        def row(label: str, value: str, bold_val: bool = False, color: str = TEXT_LIGHT):
            hl = QHBoxLayout(); hl.setSpacing(8)
            lbl = QLabel(label + ":"); lbl.setFixedWidth(140)
            lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:12px;border:none;")
            val = QLabel(value)
            w = QFont.Weight.Bold if bold_val else QFont.Weight.Normal
            val.setFont(QFont("Arial", 12, w))
            val.setStyleSheet(f"color:{color};border:none;")
            hl.addWidget(lbl); hl.addWidget(val, stretch=1)
            return hl

        # Thời gian ngay_nop có thể là "yyyy-MM-dd HH:MM:SS.ffffff" — format lại
        try:
            dt = datetime.fromisoformat(ngay_nop[:19])
            ngay_str = dt.strftime("%H:%M  %d/%m/%Y")
        except Exception:
            ngay_str = ngay_nop or "—"

        def _fmt(v): return f"{int(v):,}".replace(",", ".") + " đ"

        tt_color = SUCCESS if trang_thai_moi == "Đã nộp" else WARNING if trang_thai_moi == "Nộp thiếu" else DANGER

        for item in [
            ("Sinh viên",    ho_ten,              True,  TEXT_LIGHT),
            ("MSSV",         mssv,                False, TEXT_LIGHT),
            ("Lớp",          lop or "—",          False, TEXT_LIGHT),
            ("Khoa",         khoa or "—",         False, TEXT_LIGHT),
            ("Số tiền nộp",  _fmt(so_tien),        True,  SUCCESS),
            ("Phương thức",  phuong_thuc,         False, TEXT_LIGHT),
            ("Thời gian",    ngay_str,            False, TEXT_MUTED),
            ("Còn lại",      _fmt(con_lai) if con_lai > 0 else "Đã đóng đủ", True, tt_color),
            ("Trạng thái",   trang_thai_moi,      True,  tt_color),
        ]:
            root.addLayout(row(*item))

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine); sep2.setStyleSheet(f"color:{BORDER};")
        root.addWidget(sep2)

        if con_lai > 0:
            warn = QLabel(f"⚠  Sinh viên còn thiếu {_fmt(con_lai)} — vui lòng nộp trước hạn.")
            warn.setStyleSheet(f"color:{WARNING};font-size:12px;border:none;")
            warn.setWordWrap(True)
            root.addWidget(warn)

        root.addStretch()
        btn = QPushButton("Đóng"); btn.setFixedHeight(34); btn.clicked.connect(self.accept)
        btn.setStyleSheet(f"QPushButton{{background:{HIGHLIGHT};color:white;border:none;border-radius:6px;font-weight:700;padding:0 20px;}}QPushButton:hover{{background:#c73050;}}")
        hr = QHBoxLayout(); hr.addStretch(); hr.addWidget(btn)
        root.addLayout(hr)


class PaymentHistoryDialog(QDialog):
    def __init__(self, mssv: str, ho_ten: str):
        super().__init__()
        self._ctrl = TuitionController()
        self.setWindowTitle(f"Lịch sử thanh toán — {ho_ten}")
        self.setMinimumSize(620, 400)
        self.setStyleSheet(f"background:{PRIMARY};color:{TEXT_LIGHT};")
        self._build(mssv, ho_ten)
        self._load(mssv)

    def _build(self, mssv, ho_ten):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16); root.setSpacing(12)

        title = QLabel("Lịch sử thanh toán học phí")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        sub = QLabel(f"{ho_ten}  |  MSSV: {mssv}")
        sub.setStyleSheet(f"color:{TEXT_MUTED};font-size:12px;")
        root.addWidget(title); root.addWidget(sub)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color:{BORDER};"); root.addWidget(sep)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Ngày nộp", "Số tiền", "Phương thức", "Ghi chú"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setStyleSheet(f"background:{SECONDARY};color:{TEXT_MUTED};font-size:12px;border:none;")
        self.table.setStyleSheet(f"""
            QTableWidget{{background:{PRIMARY};border:1px solid {BORDER};border-radius:8px;gridline-color:{BORDER};}}
            QTableWidget::item{{padding:6px 10px;color:{TEXT_LIGHT};border:none;}}
            QTableWidget::item:selected{{background:#1E3A5F;}}
        """)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setColumnWidth(0, 160); self.table.setColumnWidth(1, 130); self.table.setColumnWidth(2, 130)
        root.addWidget(self.table)

        self.lbl_tong = QLabel("Tổng đã nộp: —")
        self.lbl_tong.setStyleSheet(f"color:{SUCCESS};font-size:13px;font-weight:700;")
        self.lbl_tong.setAlignment(Qt.AlignmentFlag.AlignRight)
        root.addWidget(self.lbl_tong)

        btn_close = QPushButton("Đóng"); btn_close.setFixedHeight(34)
        btn_close.setStyleSheet(f"QPushButton{{background:transparent;color:{TEXT_MUTED};border:1px solid {BORDER};border-radius:6px;padding:0 20px;}}QPushButton:hover{{color:{TEXT_LIGHT};}}")
        btn_close.clicked.connect(self.accept)
        hr = QHBoxLayout(); hr.addStretch(); hr.addWidget(btn_close)
        root.addLayout(hr)

    def _load(self, mssv):
        def ok(data):
            self.table.setRowCount(len(data))
            tong = 0.0
            for row, item in enumerate(data):
                ngay = (item.get("ngay_nop") or "")[:19]
                so_tien = item.get("so_tien", 0)
                tong += so_tien
                for col, val in enumerate([
                    ngay, fmt_money(so_tien),
                    item.get("phuong_thuc", ""), item.get("ghi_chu", "") or "",
                ]):
                    cell = QTableWidgetItem(str(val))
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                    self.table.setItem(row, col, cell)
            self.lbl_tong.setText(f"Tổng đã nộp: {fmt_money(tong)}")
            if not data:
                self.table.setRowCount(1)
                empty = QTableWidgetItem("Chưa có lịch sử thanh toán")
                empty.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                empty.setForeground(QColor(TEXT_MUTED))
                self.table.setSpan(0, 0, 1, 4)
                self.table.setItem(0, 0, empty)

        def err(msg):
            QMessageBox.warning(self, "Lỗi", msg)

        self._ctrl.load_payment_history(mssv, on_success=ok, on_error=err)
