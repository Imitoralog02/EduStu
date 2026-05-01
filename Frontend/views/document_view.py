from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton,
    QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QScrollArea, QCheckBox, QLineEdit,
    QMessageBox, QGraphicsDropShadowEffect, QTextEdit, QDateEdit,
    QDialog, QGridLayout, QComboBox, QFileDialog, QSpinBox,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QDate, QSize
from utils.helpers import fmt_date
from PyQt6.QtGui import QFont, QColor, QPixmap
from views.base_view import BaseView, QSS_INPUT, make_card
from controllers.document import DocumentController
from utils.config import SUCCESS, DANGER, WARNING, TEXT_LIGHT, TEXT_MUTED, BORDER, INFO, PRIMARY, SECONDARY, ACCENT


# ── Card sinh viên thiếu giấy tờ ─────────────────────────────────────────────
class MissingCard(QFrame):
    def __init__(self, data, on_click):
        super().__init__()
        self._data = data; self._on_click = on_click
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(52)
        self.setStyleSheet("""
            QFrame { background:rgba(239,68,68,0.08); border-radius:7px; border:1px solid rgba(239,68,68,0.25); }
            QFrame:hover { background:rgba(239,68,68,0.18); }
        """)
        lay = QHBoxLayout(self); lay.setContentsMargins(10,6,10,6); lay.setSpacing(10)
        icon = QLabel("⚠"); icon.setStyleSheet(f"color:{DANGER};font-size:14px;font-weight:700;border:none;"); icon.setFixedWidth(18)
        lay.addWidget(icon)
        info = QVBoxLayout(); info.setSpacing(1)
        name_lbl = QLabel(f"{data.ho_ten}  <span style='color:#94A3B8;font-size:11px;'>({data.mssv})</span>")
        name_lbl.setTextFormat(Qt.TextFormat.RichText)
        name_lbl.setStyleSheet(f"color:{TEXT_LIGHT};font-size:13px;font-weight:600;font-family:Arial;border:none;")
        sub_lbl = QLabel(f"Lớp: {data.lop or '—'}  ·  Khoa: {data.khoa or '—'}")
        sub_lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-family:Arial;border:none;")
        info.addWidget(name_lbl); info.addWidget(sub_lbl); lay.addLayout(info, stretch=1)
        count_lbl = QLabel(f"Thiếu {data.con_thieu}/{data.tong}")
        count_lbl.setStyleSheet(f"color:{DANGER};font-size:12px;font-weight:700;font-family:Arial;border:none;")
        lay.addWidget(count_lbl)
        btn = QPushButton("Xem →"); btn.setFixedSize(60,28); btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"QPushButton{{background:rgba(239,68,68,0.18);color:{DANGER};border:1px solid rgba(239,68,68,0.4);border-radius:5px;font-size:11px;font-weight:700;}}QPushButton:hover{{background:{DANGER};color:white;}}")
        btn.clicked.connect(lambda: on_click(data.mssv, data)); lay.addWidget(btn)

    def mousePressEvent(self, _): self._on_click(self._data.mssv, self._data)


# ── Card sinh viên cột trái ───────────────────────────────────────────────────
class StudentRow(QFrame):
    def __init__(self, data, on_click):
        super().__init__()
        self._mssv = data.mssv; self._on_click = on_click; self._data = data
        self._build(data); self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _build(self, d):
        self.setFixedHeight(66); self._apply_style(False)
        lay = QHBoxLayout(self); lay.setContentsMargins(10,8,10,8); lay.setSpacing(8)
        dot = QLabel(); dot.setFixedSize(10,10)
        color = SUCCESS if d.hoan_chinh else (WARNING if d.con_thieu <= 2 else DANGER)
        dot.setStyleSheet(f"background:{color};border-radius:5px;border:none;"); lay.addWidget(dot)
        info = QVBoxLayout(); info.setSpacing(1)
        name = QLabel(d.ho_ten); name.setStyleSheet(f"color:{TEXT_LIGHT};font-size:13px;font-weight:600;font-family:Arial;border:none;")
        line2 = QLabel(f"{d.mssv} · {d.lop or '—'}"); line2.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-family:Arial;border:none;")
        line3 = QLabel(d.khoa or "—"); line3.setStyleSheet("color:#4B91F7;font-size:10px;font-family:Arial;border:none;")
        info.addWidget(name); info.addWidget(line2); info.addWidget(line3); lay.addLayout(info, stretch=1)
        pct = QLabel(f"{d.da_nop}/{d.tong}")
        pct.setStyleSheet(f"color:{SUCCESS if d.hoan_chinh else DANGER};font-size:12px;font-weight:700;font-family:Arial;border:none;")
        lay.addWidget(pct)

    def _apply_style(self, selected: bool):
        if selected:
            self.setStyleSheet("QFrame{background:rgba(37,99,235,0.20);border-radius:8px;border-left:3px solid #2563EB;}")
        else:
            self.setStyleSheet("QFrame{background:rgba(255,255,255,0.04);border-radius:8px;border-left:3px solid transparent;}QFrame:hover{background:rgba(255,255,255,0.08);}")

    def set_selected(self, v: bool): self._apply_style(v)
    def mousePressEvent(self, _): self._on_click(self._mssv, self._data)

    @property
    def mssv(self): return self._mssv


# ── View chính ────────────────────────────────────────────────────────────────
class DocumentView(BaseView):
    PAGE_TITLE = "Giấy tờ nhân thân"
    PAGE_SUB   = "Quản lý hồ sơ & thông báo thiếu giấy tờ"

    def __init__(self):
        self._ctrl = DocumentController()
        self._selected_mssv: str | None = None
        self._selected_data = None
        self._rows: list[StudentRow] = []
        self._all_summary: list = []
        self._doc_data: list = []
        super().__init__()

    def build_ui(self):
        # Action button quản lý loại giấy tờ — chỉ admin
        from utils.session import Session
        if Session.can_do("giayto", "manage_types"):
            btn_manage = self.make_btn("⚙ Loại giấy tờ", "secondary")
            btn_manage.clicked.connect(lambda: DocTypeManagerDialog(self._ctrl, on_change=self.refresh).exec())
            self.add_action(btn_manage)

        # ── Banner cảnh báo ───────────────────────────────────────────────────
        self._banner_frame = QFrame(); self._banner_frame.setVisible(False)
        self._banner_frame.setStyleSheet("QFrame{background:rgba(239,68,68,0.10);border:1.5px solid rgba(239,68,68,0.35);border-radius:12px;}")
        banner_lay = QVBoxLayout(self._banner_frame); banner_lay.setContentsMargins(14,10,14,10); banner_lay.setSpacing(6)

        # Header banner
        banner_hdr = QHBoxLayout(); banner_hdr.setSpacing(8)
        icon_lbl = QLabel("⚠️"); icon_lbl.setStyleSheet("border:none;font-size:14px;")
        self._banner_title = QLabel("")
        self._banner_title.setStyleSheet(f"color:{DANGER};font-size:13px;font-weight:700;font-family:Arial;border:none;")
        self._banner_count = QLabel("")
        self._banner_count.setStyleSheet(f"color:{DANGER};font-size:12px;font-family:Arial;border:none;")
        self._btn_toggle = QPushButton("▼ Xem chi tiết")
        self._btn_toggle.setFixedHeight(26); self._btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_toggle.setStyleSheet(f"QPushButton{{background:rgba(239,68,68,0.15);color:{DANGER};border:1px solid rgba(239,68,68,0.3);border-radius:5px;font-size:11px;font-family:Arial;padding:0 10px;}}QPushButton:hover{{background:{DANGER};color:white;}}")
        self._btn_toggle.clicked.connect(self._toggle_banner_detail)
        banner_hdr.addWidget(icon_lbl)
        banner_hdr.addWidget(self._banner_title, stretch=1)
        banner_hdr.addWidget(self._banner_count)
        banner_hdr.addWidget(self._btn_toggle)
        banner_lay.addLayout(banner_hdr)

        # Vùng chi tiết cuộn được, chiều cao giới hạn 220px
        self._banner_scroll = QScrollArea()
        self._banner_scroll.setVisible(False)
        self._banner_scroll.setWidgetResizable(True)
        self._banner_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._banner_scroll.setFixedHeight(220)
        self._banner_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._banner_scroll.setStyleSheet("""
            QScrollArea { background:transparent; border:none; }
            QScrollBar:vertical { background:rgba(239,68,68,0.10); width:5px; border-radius:3px; }
            QScrollBar::handle:vertical { background:rgba(239,68,68,0.45); border-radius:3px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0px; }
        """)
        self._banner_detail = QWidget()
        self._banner_detail.setStyleSheet("background:transparent;")
        self._banner_detail_lay = QVBoxLayout(self._banner_detail)
        self._banner_detail_lay.setContentsMargins(0, 2, 4, 2)
        self._banner_detail_lay.setSpacing(4)
        self._banner_detail_lay.addStretch()
        self._banner_scroll.setWidget(self._banner_detail)
        banner_lay.addWidget(self._banner_scroll)
        self._root.addWidget(self._banner_frame)

        # ── Layout chính ──────────────────────────────────────────────────────
        main = QHBoxLayout(); main.setSpacing(14)

        # Cột trái
        left = QFrame(); left.setFixedWidth(270)
        left.setStyleSheet("QFrame{background:rgba(10,22,40,0.6);border-radius:14px;border:1px solid rgba(255,255,255,0.08);}")
        sh = QGraphicsDropShadowEffect(left); sh.setBlurRadius(20); sh.setOffset(0,3); sh.setColor(QColor(0,0,0,60))
        left.setGraphicsEffect(sh)
        left_lay = QVBoxLayout(left); left_lay.setContentsMargins(8,12,8,12); left_lay.setSpacing(6)
        hdr = QHBoxLayout(); hdr.setContentsMargins(4,0,4,0)
        lbl_sv = QLabel("Danh sách sinh viên"); lbl_sv.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-weight:700;font-family:Arial;border:none;")
        self._lbl_count = QLabel(""); self._lbl_count.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-family:Arial;border:none;"); self._lbl_count.setAlignment(Qt.AlignmentFlag.AlignRight)
        hdr.addWidget(lbl_sv); hdr.addWidget(self._lbl_count, stretch=1); left_lay.addLayout(hdr)
        self._inp_search = QLineEdit(); self._inp_search.setPlaceholderText("Tìm tên hoặc MSSV..."); self._inp_search.setFixedHeight(30); self._inp_search.setStyleSheet(QSS_INPUT)
        self._inp_search.textChanged.connect(self._filter_list); left_lay.addWidget(self._inp_search)
        self._cmb_khoa = QComboBox(); self._cmb_khoa.setFixedHeight(28); self._cmb_khoa.addItem("Tất cả khoa"); self._cmb_khoa.setStyleSheet(QSS_INPUT)
        self._cmb_khoa.currentIndexChanged.connect(self._filter_list); left_lay.addWidget(self._cmb_khoa)
        tab = QHBoxLayout(); tab.setSpacing(4)
        self._tab_all = self._tab_btn("Tất cả", True); self._tab_missing = self._tab_btn("Thiếu", False); self._tab_done = self._tab_btn("Đủ", False)
        self._tab_all.clicked.connect(lambda: self._set_tab("all")); self._tab_missing.clicked.connect(lambda: self._set_tab("missing")); self._tab_done.clicked.connect(lambda: self._set_tab("done"))
        for b in [self._tab_all, self._tab_missing, self._tab_done]: tab.addWidget(b)
        left_lay.addLayout(tab); self._current_tab = "all"
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame); scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        self._list_widget = QWidget(); self._list_widget.setStyleSheet("background:transparent;")
        self._list_lay = QVBoxLayout(self._list_widget); self._list_lay.setContentsMargins(0,0,0,0); self._list_lay.setSpacing(3); self._list_lay.addStretch()
        scroll.setWidget(self._list_widget); left_lay.addWidget(scroll); main.addWidget(left)

        # Cột phải
        right = QVBoxLayout(); right.setSpacing(10)
        self._info_card = make_card(radius=12); self._info_card.setFixedHeight(100)
        il = QHBoxLayout(self._info_card); il.setContentsMargins(18, 10, 18, 10); il.setSpacing(12)

        info_col = QVBoxLayout(); info_col.setSpacing(3)
        self._lbl_sv_name = QLabel("Chọn sinh viên để xem giấy tờ")
        self._lbl_sv_name.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self._lbl_sv_name.setStyleSheet("color:#0F172A;border:none;")
        self._lbl_sv_meta = QLabel("")
        self._lbl_sv_meta.setStyleSheet("color:#64748B;font-size:12px;font-family:Arial;border:none;")
        self._lbl_sv_stat = QLabel("")
        self._lbl_sv_stat.setStyleSheet("font-size:13px;font-family:Arial;border:none;")
        info_col.addWidget(self._lbl_sv_name)
        info_col.addWidget(self._lbl_sv_meta)
        info_col.addWidget(self._lbl_sv_stat)
        il.addLayout(info_col, stretch=1)

        self._btn_view_profile = QPushButton("👤  Xem hồ sơ đầy đủ")
        self._btn_view_profile.setFixedSize(170, 40)
        self._btn_view_profile.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_view_profile.setVisible(False)
        self._btn_view_profile.setStyleSheet(
            f"QPushButton{{background:{ACCENT};color:white;border:none;border-radius:8px;"
            f"font-size:13px;font-weight:600;font-family:Arial;}}"
            f"QPushButton:hover{{background:#1D4ED8;}}"
        )
        self._btn_view_profile.clicked.connect(self._open_profile)
        il.addWidget(self._btn_view_profile)
        right.addWidget(self._info_card)

        doc_card = make_card(radius=12); dl = QVBoxLayout(doc_card); dl.setContentsMargins(0,0,0,0)
        self._doc_table = QTableWidget()
        self._doc_table.setColumnCount(6)
        self._doc_table.setHorizontalHeaderLabels(["Loại giấy tờ", "Trạng thái", "Ngày nộp", "File đính kèm", "Ghi chú", "Thao tác"])
        self._doc_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._doc_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._doc_table.verticalHeader().setVisible(False)
        self._doc_table.setAlternatingRowColors(True)
        self._doc_table.horizontalHeader().setStretchLastSection(False)
        self._doc_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._doc_table.setColumnWidth(1, 100); self._doc_table.setColumnWidth(2, 90)
        self._doc_table.setColumnWidth(3, 160); self._doc_table.setColumnWidth(4, 140)
        self._doc_table.setColumnWidth(5, 155)
        self._doc_table.verticalHeader().setDefaultSectionSize(44)
        self._doc_table.setStyleSheet("""
            QTableWidget { background:#FFFFFF; border:none; color:#1E293B; font-size:13px; font-family:Arial; gridline-color:#F1F5F9; }
            QTableWidget::item { padding:6px 10px; }
            QTableWidget::item:selected { background:#DBEAFE; color:#1E3A8A; }
            QTableWidget::item:alternate { background:#F8FAFC; }
            QHeaderView::section { background:#F1F5F9; color:#475569; font-size:11px; font-weight:700; font-family:Arial; padding:8px 10px; border:none; border-bottom:2px solid #E2E8F0; }
        """)
        dl.addWidget(self._doc_table); right.addWidget(doc_card)
        main.addLayout(right, stretch=1); self._root.addLayout(main)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _tab_btn(self, text: str, active: bool) -> QPushButton:
        btn = QPushButton(text); btn.setFixedHeight(26); btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_tab(btn, active); return btn

    def _style_tab(self, btn, active):
        if active:
            btn.setStyleSheet(f"QPushButton{{background:{INFO};color:white;border:none;border-radius:5px;font-size:11px;font-family:Arial;font-weight:700;padding:0 8px;}}")
        else:
            btn.setStyleSheet(f"QPushButton{{background:rgba(255,255,255,0.06);color:{TEXT_MUTED};border:1px solid rgba(255,255,255,0.12);border-radius:5px;font-size:11px;font-family:Arial;padding:0 8px;}}QPushButton:hover{{color:{TEXT_LIGHT};}}")

    def _set_tab(self, tab):
        self._current_tab = tab
        self._style_tab(self._tab_all,     tab == "all")
        self._style_tab(self._tab_missing, tab == "missing")
        self._style_tab(self._tab_done,    tab == "done")
        self._filter_list()

    def _toggle_banner_detail(self):
        v = not self._banner_scroll.isVisible()
        self._banner_scroll.setVisible(v)
        self._btn_toggle.setText("▲ Thu gọn" if v else "▼ Xem chi tiết")

    # ── Data ──────────────────────────────────────────────────────────────────

    def refresh(self):
        self.run_async(self._ctrl._svc.get_summary, self._render_list, loading_text="Đang tải...")

    def _render_list(self, summary: list):
        self._all_summary = summary
        khoa_set = sorted({s.khoa for s in summary if s.khoa})
        self._cmb_khoa.blockSignals(True)
        cur = self._cmb_khoa.currentText()
        self._cmb_khoa.clear(); self._cmb_khoa.addItem("Tất cả khoa")
        for k in khoa_set: self._cmb_khoa.addItem(k)
        idx = self._cmb_khoa.findText(cur)
        self._cmb_khoa.setCurrentIndex(idx if idx >= 0 else 0)
        self._cmb_khoa.blockSignals(False)

        thieu = [s for s in summary if not s.hoan_chinh]
        if thieu:
            self._banner_frame.setVisible(True)
            self._banner_title.setText(f"Có {len(thieu)} sinh viên chưa nộp đủ giấy tờ")
            self._banner_count.setText(f"({len(thieu)} sinh viên)")
            # Xóa các card cũ (trừ stretch ở cuối)
            for i in reversed(range(self._banner_detail_lay.count())):
                item = self._banner_detail_lay.itemAt(i)
                w = item.widget() if item else None
                if w:
                    w.setParent(None)
            for sv in thieu:
                self._banner_detail_lay.insertWidget(
                    self._banner_detail_lay.count() - 1,
                    MissingCard(sv, self._select_student_and_scroll)
                )
            # Thu gọn lại khi data mới load
            self._banner_scroll.setVisible(False)
            self._btn_toggle.setText("▼ Xem chi tiết")
        else:
            self._banner_frame.setVisible(False)
            self._banner_scroll.setVisible(False)
        self._filter_list()

    def _filter_list(self):
        if not self._all_summary: return
        search = self._inp_search.text().strip().lower()
        khoa_f = self._cmb_khoa.currentText() if self._cmb_khoa.currentIndex() > 0 else ""
        filtered = []
        for s in self._all_summary:
            if search and search not in s.ho_ten.lower() and search not in s.mssv.lower(): continue
            if khoa_f and (s.khoa or "") != khoa_f: continue
            if self._current_tab == "missing" and s.hoan_chinh: continue
            if self._current_tab == "done" and not s.hoan_chinh: continue
            filtered.append(s)
        thieu_count = sum(1 for s in self._all_summary if not s.hoan_chinh)
        self._lbl_count.setText(f"{thieu_count} thiếu / {len(self._all_summary)}")
        for row in self._rows: row.setParent(None)
        self._rows.clear()
        for s in filtered:
            row = StudentRow(s, self._select_student)
            if s.mssv == self._selected_mssv: row.set_selected(True)
            self._list_lay.insertWidget(self._list_lay.count() - 1, row)
            self._rows.append(row)

    def _select_student_and_scroll(self, mssv, data):
        self._banner_scroll.setVisible(False); self._btn_toggle.setText("▼ Xem chi tiết")
        self._set_tab("all")
        if self._cmb_khoa.currentIndex() > 0:
            idx = self._cmb_khoa.findText(data.khoa or "")
            self._cmb_khoa.setCurrentIndex(idx if idx >= 0 else 0)
        self._select_student(mssv, data)

    def _select_student(self, mssv, data):
        self._selected_mssv = mssv
        self._selected_data = data
        for row in self._rows: row.set_selected(row.mssv == mssv)
        khoa = data.khoa or "—"; lop = data.lop or "—"
        self._lbl_sv_name.setText(data.ho_ten)
        self._lbl_sv_meta.setText(f"MSSV: {mssv}  ·  Lớp: {lop}  ·  Khoa: {khoa}")
        clr = SUCCESS if data.hoan_chinh else DANGER
        status = "✓  Đầy đủ hồ sơ" if data.hoan_chinh else f"⚠  Còn thiếu {data.con_thieu} giấy tờ"
        self._lbl_sv_stat.setText(f"<span style='color:{clr};font-weight:700;font-size:13px;'>{data.da_nop}/{data.tong} — {status}</span>")
        self._lbl_sv_stat.setTextFormat(Qt.TextFormat.RichText)
        self._btn_view_profile.setVisible(True)
        self.run_async(lambda: self._ctrl._svc.get_docs(mssv), self._render_docs, loading_text="Đang tải giấy tờ...")

    def _open_profile(self):
        if not self._selected_mssv:
            return
        try:
            from controllers.student import StudentController
            raw = StudentController()._svc.get_by_mssv(self._selected_mssv)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", str(e))
            return
        from views.student_view import StudentProfileDialog
        StudentProfileDialog(data=raw).exec()

    def _render_docs(self, docs: list):
        self._doc_data = docs
        self._doc_table.setRowCount(len(docs))
        for r, d in enumerate(docs):
            # Cột 0: Loại giấy
            loai = QTableWidgetItem(d.loai_giay)
            loai.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self._doc_table.setItem(r, 0, loai)

            # Cột 1: Trạng thái
            tt_text = "✓  Đã nộp" if d.da_nop else "✗  Chưa nộp"
            tt_item = QTableWidgetItem(tt_text)
            tt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tt_item.setForeground(QColor(SUCCESS if d.da_nop else DANGER))
            tt_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self._doc_table.setItem(r, 1, tt_item)

            # Cột 2: Ngày nộp
            ngay = QTableWidgetItem(d.ngay_nop or "—"); ngay.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._doc_table.setItem(r, 2, ngay)

            # Cột 3: File đính kèm
            file_w = QWidget(); file_hl = QHBoxLayout(file_w); file_hl.setContentsMargins(4,4,4,4); file_hl.setSpacing(4)
            if d.has_file:
                file_lbl = QLabel(f"📎 {d.file_name}")
                file_lbl.setStyleSheet(f"color:{INFO};font-size:11px;")
                file_lbl.setToolTip(f"{d.file_name} ({d.file_size_display})")
                btn_view = QPushButton("Xem"); btn_view.setFixedHeight(24)
                btn_view.setStyleSheet(f"QPushButton{{background:{INFO};color:white;border:none;border-radius:4px;font-size:10px;padding:0 8px;}}QPushButton:hover{{background:#1D4ED8;}}")
                btn_view.clicked.connect(lambda _, doc=d: self._preview_file(doc))
                btn_dl = QPushButton("⬇"); btn_dl.setFixedSize(24, 24)
                btn_dl.setToolTip("Tải về máy")
                btn_dl.setStyleSheet(f"QPushButton{{background:transparent;color:{SUCCESS};border:1px solid {SUCCESS};border-radius:4px;font-size:10px;}}QPushButton:hover{{background:{SUCCESS};color:white;}}")
                btn_dl.clicked.connect(lambda _, doc=d: self._download_file(doc))
                btn_del = QPushButton("✕"); btn_del.setFixedSize(24, 24)
                btn_del.setStyleSheet(f"QPushButton{{background:transparent;color:{DANGER};border:1px solid {DANGER};border-radius:4px;font-size:10px;}}QPushButton:hover{{background:{DANGER};color:white;}}")
                btn_del.clicked.connect(lambda _, doc=d: self._delete_file(doc))
                file_hl.addWidget(file_lbl, stretch=1); file_hl.addWidget(btn_view); file_hl.addWidget(btn_dl); file_hl.addWidget(btn_del)
            else:
                btn_up = QPushButton("⬆ Tải lên"); btn_up.setFixedHeight(26)
                btn_up.setStyleSheet(f"QPushButton{{background:transparent;color:{WARNING};border:1px solid {WARNING};border-radius:4px;font-size:11px;padding:0 8px;}}QPushButton:hover{{background:{WARNING};color:white;}}")
                btn_up.clicked.connect(lambda _, doc=d: self._upload_file(doc))
                file_hl.addWidget(btn_up)
            self._doc_table.setCellWidget(r, 3, file_w)

            # Cột 4: Ghi chú
            self._doc_table.setItem(r, 4, QTableWidgetItem(d.ghi_chu or ""))

            # Cột 5: Thao tác
            from utils.session import Session
            action_w = QWidget(); action_hl = QHBoxLayout(action_w); action_hl.setContentsMargins(4,4,4,4); action_hl.setSpacing(4)
            if Session.can_do("giayto", "edit"):
                btn_update = QPushButton("Cập nhật"); btn_update.setFixedHeight(28); btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_update.setStyleSheet(f"QPushButton{{background:{INFO};color:white;border:none;border-radius:5px;font-size:11px;padding:0 10px;}}QPushButton:hover{{background:#1D4ED8;}}")
                btn_update.clicked.connect(lambda _, doc=d: self._open_update(doc))
                action_hl.addWidget(btn_update)
            self._doc_table.setCellWidget(r, 5, action_w)

    def _open_update(self, doc):
        dlg = DocUpdateDialog(doc, on_save=lambda **kw: self._save_doc(doc.id, **kw))
        dlg.exec()

    def _save_doc(self, doc_id, da_nop, ngay_nop, ghi_chu):
        def reload_docs(_):
            if not self._selected_mssv:
                return
            def reload_summary(_docs):
                self._render_docs(_docs)
                self.run_async(self._ctrl._svc.get_summary, self._render_list)
            self.run_async(
                lambda: self._ctrl._svc.get_docs(self._selected_mssv),
                reload_summary,
            )
        self.run_async(
            lambda: self._ctrl._svc.update_doc(doc_id, da_nop, ngay_nop, ghi_chu),
            reload_docs,
            loading_text="Đang lưu...",
        )

    def _upload_file(self, doc):
        path, _ = QFileDialog.getOpenFileName(
            self, f"Tải lên — {doc.loai_giay}", "",
            "Tài liệu (*.pdf *.jpg *.jpeg *.png)",
        )
        if not path: return

        def ok(updated_doc):
            QMessageBox.information(self, "Thành công", f"Đã tải lên file:\n{updated_doc.file_name}\nTrạng thái đã được cập nhật thành Đã nộp.")
            if self._selected_mssv:
                def reload_summary(_docs):
                    self._render_docs(_docs)
                    self.run_async(self._ctrl._svc.get_summary, self._render_list)
                self.run_async(lambda: self._ctrl._svc.get_docs(self._selected_mssv), reload_summary)

        def err(msg): QMessageBox.warning(self, "Lỗi tải file", msg)
        self._ctrl.upload_file(doc.id, path, on_success=ok, on_error=err)

    def _delete_file(self, doc):
        reply = QMessageBox.question(self, "Xác nhận", f"Xóa file đính kèm của '{doc.loai_giay}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes: return

        def ok(_):
            if self._selected_mssv:
                self.run_async(lambda: self._ctrl._svc.get_docs(self._selected_mssv), self._render_docs)

        self._ctrl.delete_file(doc.id, on_success=ok, on_error=lambda msg: QMessageBox.warning(self, "Lỗi", msg))

    def _preview_file(self, doc):
        """Xem trước file: ảnh hiển thị ngay trong app, file khác mở bằng ứng dụng hệ thống."""
        mime = (doc.mime_type or "").lower()
        is_image = any(mime.startswith(t) for t in ("image/jpeg", "image/png", "image/gif", "image/bmp", "image/webp"))

        def ok(raw: bytes):
            if is_image:
                FilePreviewDialog(doc.file_name or "file", raw, parent=self).exec()
            else:
                # Không phải ảnh — ghi tạm ra temp rồi mở
                import tempfile, os, pathlib
                suffix = pathlib.Path(doc.file_name or "file").suffix or ".tmp"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
                    f.write(raw)
                    tmp_path = f.name
                try:
                    os.startfile(tmp_path)
                except Exception as e:
                    QMessageBox.warning(self, "Không thể mở", str(e))

        self._ctrl.download_file(doc.id, on_success=ok,
                                 on_error=lambda msg: QMessageBox.warning(self, "Lỗi tải file", msg))

    def _download_file(self, doc):
        save_path, _ = QFileDialog.getSaveFileName(
            self, f"Lưu file — {doc.loai_giay}", doc.file_name or "file",
            "Tất cả file (*.*)"
        )
        if not save_path: return

        def ok(raw: bytes):
            import os
            with open(save_path, "wb") as f:
                f.write(raw)
            reply = QMessageBox.information(
                self, "Tải về thành công",
                f"Đã lưu file:\n{save_path}",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Open,
            )
            if reply == QMessageBox.StandardButton.Open:
                os.startfile(os.path.dirname(save_path))

        self._ctrl.download_file(doc.id, on_success=ok,
                                 on_error=lambda msg: QMessageBox.warning(self, "Lỗi tải về", msg))


# ── Dialog quản lý loại giấy tờ ──────────────────────────────────────────────
class DocTypeManagerDialog(QDialog):
    def __init__(self, ctrl: DocumentController, on_change=None):
        super().__init__()
        self._ctrl      = ctrl
        self._on_change = on_change
        self._types: list = []
        self.setWindowTitle("Quản lý loại giấy tờ")
        self.setMinimumSize(680, 480)
        self.setStyleSheet("background:#FFFFFF;color:#1E293B;font-family:Arial;")
        self._build()
        self._load()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(20,16,20,16); root.setSpacing(12)
        title = QLabel("Loại giấy tờ yêu cầu"); title.setFont(QFont("Arial", 14, QFont.Weight.Bold)); title.setStyleSheet("color:#0F172A;")
        note  = QLabel("Thêm/sửa/xóa loại giấy tờ. Thay đổi sẽ áp dụng cho tất cả sinh viên khi tải lại.")
        note.setStyleSheet("color:#64748B;font-size:12px;")
        root.addWidget(title); root.addWidget(note)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet("color:#E2E8F0;"); root.addWidget(sep)

        # Bảng
        self.table = QTableWidget(); self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Tên loại giấy tờ", "Bắt buộc", "Mô tả / hướng dẫn", "Thứ tự", ""])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 180); self.table.setColumnWidth(1, 70); self.table.setColumnWidth(3, 60); self.table.setColumnWidth(4, 130)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;gridline-color:#F1F5F9;font-size:13px;}
            QTableWidget::item{padding:6px 10px;}
            QTableWidget::item:selected{background:#DBEAFE;color:#1E3A8A;}
            QTableWidget::item:alternate{background:#F8FAFC;}
            QHeaderView::section{background:#F1F5F9;color:#475569;font-size:11px;font-weight:700;padding:8px 10px;border:none;border-bottom:2px solid #E2E8F0;}
        """)
        root.addWidget(self.table)

        # Form thêm mới
        add_box = QFrame(); add_box.setStyleSheet("QFrame{background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;}")
        add_lay = QGridLayout(add_box); add_lay.setContentsMargins(14,12,14,12); add_lay.setSpacing(10)
        def lbl(t): l = QLabel(t); l.setStyleSheet("color:#475569;font-size:12px;font-weight:600;"); return l

        self.f_ten   = QLineEdit(); self.f_ten.setPlaceholderText("VD: Giấy khám sức khỏe"); self.f_ten.setFixedHeight(34); self.f_ten.setStyleSheet("QLineEdit{background:#FFF;border:1.5px solid #E2E8F0;border-radius:7px;padding:0 10px;}QLineEdit:focus{border-color:#2563EB;}")
        self.f_mo_ta = QLineEdit(); self.f_mo_ta.setPlaceholderText("Hướng dẫn nộp (tùy chọn)"); self.f_mo_ta.setFixedHeight(34); self.f_mo_ta.setStyleSheet("QLineEdit{background:#FFF;border:1.5px solid #E2E8F0;border-radius:7px;padding:0 10px;}QLineEdit:focus{border-color:#2563EB;}")
        self.f_bb    = QCheckBox("Bắt buộc"); self.f_bb.setChecked(True); self.f_bb.setStyleSheet("color:#1E293B;font-size:13px;")
        self.f_thu_tu = QSpinBox(); self.f_thu_tu.setRange(0, 999); self.f_thu_tu.setFixedHeight(34); self.f_thu_tu.setStyleSheet("QSpinBox{background:#FFF;border:1.5px solid #E2E8F0;border-radius:7px;padding:0 6px;}QSpinBox:focus{border-color:#2563EB;}")

        btn_add = QPushButton("+ Thêm"); btn_add.setFixedHeight(34); btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet(f"QPushButton{{background:#2563EB;color:white;border:none;border-radius:7px;font-weight:700;padding:0 18px;}}QPushButton:hover{{background:#1D4ED8;}}")
        btn_add.clicked.connect(self._add)

        add_lay.addWidget(lbl("Tên *"), 0, 0); add_lay.addWidget(self.f_ten, 0, 1)
        add_lay.addWidget(lbl("Mô tả"), 0, 2); add_lay.addWidget(self.f_mo_ta, 0, 3)
        add_lay.addWidget(self.f_bb, 1, 0); add_lay.addWidget(lbl("Thứ tự"), 1, 2); add_lay.addWidget(self.f_thu_tu, 1, 3)
        add_lay.addWidget(btn_add, 1, 4)
        root.addWidget(add_box)

        btn_close = QPushButton("Đóng"); btn_close.setFixedHeight(34); btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet("QPushButton{background:transparent;color:#475569;border:1px solid #E2E8F0;border-radius:7px;padding:0 20px;}QPushButton:hover{background:#F1F5F9;}")
        hr = QHBoxLayout(); hr.addStretch(); hr.addWidget(btn_close); root.addLayout(hr)

    def _load(self):
        def ok(types):
            self._types = types
            self.table.setRowCount(len(types))
            for r, dt in enumerate(types):
                self.table.setItem(r, 0, QTableWidgetItem(dt.ten_loai))
                bb = QTableWidgetItem("✓" if dt.bat_buoc else "—"); bb.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                bb.setForeground(QColor(SUCCESS if dt.bat_buoc else TEXT_MUTED)); self.table.setItem(r, 1, bb)
                self.table.setItem(r, 2, QTableWidgetItem(dt.mo_ta or ""))
                tt = QTableWidgetItem(str(dt.thu_tu)); tt.setTextAlignment(Qt.AlignmentFlag.AlignCenter); self.table.setItem(r, 3, tt)
                # Nút sửa + xóa
                w = QWidget(); hl = QHBoxLayout(w); hl.setContentsMargins(4,4,4,4); hl.setSpacing(4)
                btn_edit = QPushButton("Sửa"); btn_edit.setFixedHeight(26)
                btn_edit.setStyleSheet(f"QPushButton{{background:transparent;color:{ACCENT};border:1px solid {ACCENT};border-radius:4px;font-size:11px;padding:0 8px;}}QPushButton:hover{{background:{ACCENT};color:white;}}")
                btn_edit.clicked.connect(lambda _, t=dt: self._edit(t))
                btn_del = QPushButton("Xóa"); btn_del.setFixedHeight(26)
                btn_del.setStyleSheet(f"QPushButton{{background:transparent;color:{DANGER};border:1px solid {DANGER};border-radius:4px;font-size:11px;padding:0 8px;}}QPushButton:hover{{background:{DANGER};color:white;}}")
                btn_del.clicked.connect(lambda _, t=dt: self._delete(t))
                hl.addWidget(btn_edit); hl.addWidget(btn_del); self.table.setCellWidget(r, 4, w)
        self._ctrl.load_doc_types(on_success=ok, on_error=lambda msg: QMessageBox.warning(self, "Lỗi", msg))

    def _add(self):
        ten = self.f_ten.text().strip()
        if not ten: QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên loại giấy tờ."); return

        def ok(_):
            self.f_ten.clear(); self.f_mo_ta.clear(); self.f_bb.setChecked(True); self.f_thu_tu.setValue(0)
            self._load()
            if self._on_change: self._on_change()

        self._ctrl.create_doc_type(ten, self.f_bb.isChecked(), self.f_mo_ta.text().strip(), self.f_thu_tu.value(),
                                   on_success=ok, on_error=lambda msg: QMessageBox.warning(self, "Lỗi", msg))

    def _edit(self, dt):
        dlg = DocTypeEditDialog(dt, self._ctrl, on_save=lambda: (self._load(), self._on_change() if self._on_change else None))
        dlg.exec()

    def _delete(self, dt):
        reply = QMessageBox.question(self, "Xác nhận xóa",
            f"Xóa loại giấy '{dt.ten_loai}'?\n\nThao tác này cũng xóa tất cả bản ghi giấy tờ loại này của mọi sinh viên.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes: return

        def ok(_):
            self._load()
            if self._on_change: self._on_change()

        self._ctrl.delete_doc_type(dt.id, on_success=ok, on_error=lambda msg: QMessageBox.warning(self, "Lỗi", msg))


# ── Dialog sửa loại giấy tờ ──────────────────────────────────────────────────
class DocTypeEditDialog(QDialog):
    def __init__(self, dt, ctrl: DocumentController, on_save=None):
        super().__init__()
        self._dt = dt; self._ctrl = ctrl; self._on_save = on_save
        self.setWindowTitle(f"Sửa — {dt.ten_loai}"); self.setFixedSize(420, 250)
        self.setStyleSheet("background:#FFFFFF;color:#1E293B;font-family:Arial;")
        self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(24,20,24,20); root.setSpacing(12)
        title = QLabel(f"Sửa loại giấy tờ"); title.setFont(QFont("Arial", 13, QFont.Weight.Bold)); title.setStyleSheet("color:#0F172A;"); root.addWidget(title)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet("color:#E2E8F0;"); root.addWidget(sep)

        grid = QGridLayout(); grid.setSpacing(10)
        def lbl(t): l = QLabel(t); l.setStyleSheet("color:#475569;font-size:12px;font-weight:600;"); return l

        self.f_ten = QLineEdit(self._dt.ten_loai); self.f_ten.setFixedHeight(34); self.f_ten.setStyleSheet("QLineEdit{background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:7px;padding:0 10px;}QLineEdit:focus{border-color:#2563EB;}")
        self.f_mota = QLineEdit(self._dt.mo_ta or ""); self.f_mota.setFixedHeight(34); self.f_mota.setStyleSheet("QLineEdit{background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:7px;padding:0 10px;}QLineEdit:focus{border-color:#2563EB;}")
        self.f_bb = QCheckBox("Bắt buộc"); self.f_bb.setChecked(self._dt.bat_buoc); self.f_bb.setStyleSheet("color:#1E293B;font-size:13px;")
        self.f_thu_tu = QSpinBox(); self.f_thu_tu.setRange(0,999); self.f_thu_tu.setValue(self._dt.thu_tu); self.f_thu_tu.setFixedHeight(34); self.f_thu_tu.setStyleSheet("QSpinBox{background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:7px;padding:0 6px;}")

        grid.addWidget(lbl("Tên *"), 0, 0); grid.addWidget(self.f_ten, 0, 1)
        grid.addWidget(lbl("Mô tả"), 1, 0); grid.addWidget(self.f_mota, 1, 1)
        grid.addWidget(self.f_bb, 2, 0); grid.addWidget(lbl("Thứ tự"), 2, 1)
        grid.addWidget(self.f_thu_tu, 3, 1)
        root.addLayout(grid); root.addStretch()

        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Hủy"); bc.setFixedHeight(34); bc.clicked.connect(self.reject)
        bc.setStyleSheet("QPushButton{background:transparent;color:#475569;border:1px solid #E2E8F0;border-radius:7px;padding:0 16px;}")
        bs = QPushButton("Lưu"); bs.setFixedHeight(34); bs.clicked.connect(self._save)
        bs.setStyleSheet(f"QPushButton{{background:#2563EB;color:white;border:none;border-radius:7px;font-weight:700;padding:0 20px;}}QPushButton:hover{{background:#1D4ED8;}}")
        btn_row.addWidget(bc); btn_row.addWidget(bs); root.addLayout(btn_row)

    def _save(self):
        ten = self.f_ten.text().strip()
        if not ten: QMessageBox.warning(self, "Lỗi", "Tên không được trống."); return
        data = {"ten_loai": ten, "bat_buoc": self.f_bb.isChecked(), "mo_ta": self.f_mota.text().strip() or None, "thu_tu": self.f_thu_tu.value()}

        def ok(_):
            if self._on_save: self._on_save()
            self.accept()
        self._ctrl.update_doc_type(self._dt.id, data, on_success=ok, on_error=lambda msg: QMessageBox.warning(self, "Lỗi", msg))


# ── Dialog cập nhật trạng thái giấy tờ ───────────────────────────────────────
class DocUpdateDialog(QDialog):
    def __init__(self, doc, on_save):
        super().__init__()
        self._doc = doc; self._on_save = on_save
        self.setWindowTitle(f"Cập nhật — {doc.loai_giay}")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background:#FFFFFF;color:#1E293B;font-family:Arial;")
        self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(24,20,24,20); root.setSpacing(14)
        title = QLabel(self._doc.loai_giay); title.setFont(QFont("Arial", 14, QFont.Weight.Bold)); title.setStyleSheet("color:#0F172A;"); root.addWidget(title)
        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine); sep.setStyleSheet("color:#E2E8F0;"); root.addWidget(sep)

        grid = QGridLayout(); grid.setSpacing(10)
        def lbl(t): l = QLabel(t); l.setStyleSheet("color:#475569;font-size:12px;font-weight:600;"); return l

        self._chk = QCheckBox("Đã nộp"); self._chk.setChecked(self._doc.da_nop); self._chk.setStyleSheet("color:#1E293B;font-size:13px;")
        self._date = QDateEdit(); self._date.setCalendarPopup(True); self._date.setFixedHeight(34); self._date.setEnabled(self._doc.da_nop)
        self._date.setStyleSheet("QDateEdit{background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:8px;padding:0 10px;font-size:13px;color:#1E293B;}QDateEdit:focus{border-color:#2563EB;}QDateEdit:disabled{background:#F1F5F9;color:#94A3B8;}")
        if self._doc.ngay_nop:
            try:
                parts = self._doc.ngay_nop.split("-")
                self._date.setDate(QDate(int(parts[0]), int(parts[1]), int(parts[2])))
            except Exception:
                self._date.setDate(QDate.currentDate())
        else:
            self._date.setDate(QDate.currentDate())

        self._chk.toggled.connect(self._date.setEnabled)
        self._chk.toggled.connect(self._on_check_toggle)

        self._note = QTextEdit(); self._note.setFixedHeight(60); self._note.setPlaceholderText("Ghi chú..."); self._note.setText(self._doc.ghi_chu or "")
        self._note.setStyleSheet("QTextEdit{background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:8px;padding:6px 10px;font-size:13px;color:#1E293B;}")

        grid.addWidget(lbl("Trạng thái"), 0, 0); grid.addWidget(self._chk, 0, 1)
        grid.addWidget(lbl("Ngày nộp"),   1, 0); grid.addWidget(self._date, 1, 1)
        grid.addWidget(lbl("Ghi chú"),    2, 0); grid.addWidget(self._note, 2, 1)
        root.addLayout(grid); root.addStretch()

        hint_text = "✓ Đã nộp" if self._doc.da_nop else "✗ Chưa nộp"
        hint_clr  = SUCCESS if self._doc.da_nop else DANGER
        self._hint = QLabel(f"Trạng thái hiện tại: <b style='color:{hint_clr}'>{hint_text}</b>")
        self._hint.setTextFormat(Qt.TextFormat.RichText); self._hint.setStyleSheet("font-size:12px;color:#64748B;")
        root.addWidget(self._hint)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Hủy"); bc.setFixedHeight(34); bc.clicked.connect(self.reject)
        bc.setStyleSheet("QPushButton{background:transparent;color:#475569;border:1px solid #E2E8F0;border-radius:7px;padding:0 16px;}")
        bs = QPushButton("Lưu"); bs.setFixedHeight(34); bs.clicked.connect(self._save)
        bs.setStyleSheet(f"QPushButton{{background:{INFO};color:white;border:none;border-radius:7px;font-weight:700;padding:0 20px;}}QPushButton:hover{{background:#1D4ED8;}}")
        btn_row.addWidget(bc); btn_row.addWidget(bs); root.addLayout(btn_row)

    def _on_check_toggle(self, checked):
        clr = SUCCESS if checked else DANGER
        self._hint.setText(f"Trạng thái mới: <b style='color:{clr}'>{'✓ Đã nộp' if checked else '✗ Chưa nộp'}</b>")

    def _save(self):
        da_nop  = self._chk.isChecked()
        qd      = self._date.date()
        ngay    = f"{qd.year()}-{qd.month():02d}-{qd.day():02d}" if da_nop else None
        ghi_chu = self._note.toPlainText().strip() or None
        self._on_save(da_nop=da_nop, ngay_nop=ngay, ghi_chu=ghi_chu)
        self.accept()


# ── Dialog xem trước file ảnh ─────────────────────────────────────────────────
class FilePreviewDialog(QDialog):
    """Hiển thị ảnh trực tiếp trong app (JPEG, PNG, GIF, BMP, WEBP)."""

    MAX_W = 900
    MAX_H = 680

    def __init__(self, file_name: str, raw: bytes, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Xem trước — {file_name}")
        self.setStyleSheet("background:#1E293B;")
        self._build(raw, file_name)

    def _build(self, raw: bytes, file_name: str):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # Tên file
        name_lbl = QLabel(file_name)
        name_lbl.setStyleSheet("color:#94A3B8;font-size:12px;font-family:Arial;border:none;")
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(name_lbl)

        # Ảnh
        pixmap = QPixmap()
        pixmap.loadFromData(raw)

        if pixmap.isNull():
            err = QLabel("Không thể hiển thị ảnh này.")
            err.setStyleSheet("color:#FCA5A5;font-size:14px;font-family:Arial;border:none;")
            err.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(err)
        else:
            scaled = pixmap.scaled(
                QSize(self.MAX_W, self.MAX_H),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            img_lbl = QLabel()
            img_lbl.setPixmap(scaled)
            img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_lbl.setStyleSheet("border:none;background:transparent;")
            root.addWidget(img_lbl)
            self.resize(scaled.width() + 24, scaled.height() + 80)

        # Nút đóng
        btn_close = QPushButton("Đóng")
        btn_close.setFixedHeight(34)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(
            "QPushButton{background:transparent;color:#94A3B8;border:1px solid #475569;"
            "border-radius:7px;font-size:13px;padding:0 24px;}"
            "QPushButton:hover{color:#F1F5F9;border-color:#94A3B8;}"
        )
        btn_close.clicked.connect(self.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch(); btn_row.addWidget(btn_close); btn_row.addStretch()
        root.addLayout(btn_row)


# ── Hằng số & helper dùng chung ──────────────────────────────────────────────

LOAI_GIAY_YEU_CAU = [
    "CCCD/CMND", "Giấy khai sinh", "Học bạ THPT",
    "Bằng tốt nghiệp THPT", "Ảnh thẻ 3x4", "Sổ hộ khẩu",
]


def show_required_docs_notice(parent):
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


def _clear_doc_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w:
            w.deleteLater()
        elif item.layout():
            _clear_doc_layout(item.layout())


def _doc_tbl_item(text: str, center: bool = False, bold: bool = False) -> QTableWidgetItem:
    it = QTableWidgetItem(str(text) if text is not None else "")
    if center:
        it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    if bold:
        f = it.font(); f.setBold(True); it.setFont(f)
    return it


# ── Widget: Tab Giấy tờ nhúng trong StudentProfileDialog ─────────────────────

class StudentDocTab(QWidget):
    """Tab Giấy tờ dùng trong StudentProfileDialog."""

    def __init__(self, mssv: str, alert_layout: QVBoxLayout):
        super().__init__()
        self._mssv         = mssv
        self._docs         = []
        self._alert_layout = alert_layout
        self._ctrl         = DocumentController()
        self._workers: list = []
        self.setStyleSheet("background:#FFFFFF;")
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(16, 12, 16, 12)
        self._lay.setSpacing(8)
        loading = QLabel("Đang tải...")
        loading.setStyleSheet(f"color:#94A3B8;font-size:13px;font-family:Arial;border:none;")
        loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lay.addWidget(loading)

    def load(self):
        from controllers.base import ApiWorker
        w = ApiWorker(lambda: self._ctrl._svc.get_docs(self._mssv) or [])
        w.success.connect(self._on_loaded)
        w.start()
        self._workers.append(w)

    def _on_loaded(self, docs):
        self._docs = docs or []
        self._populate()
        self._refresh_alert()

    def _refresh_alert(self):
        _clear_doc_layout(self._alert_layout)
        missing = [d for d in self._docs if not d.da_nop]
        if not missing:
            return
        alert = QFrame()
        alert.setStyleSheet(
            "QFrame{background:#FEF2F2;border:1px solid #FECACA;"
            "border-radius:8px;margin-bottom:8px;}"
        )
        al = QHBoxLayout(alert)
        al.setContentsMargins(14, 10, 14, 10)
        warn = QLabel(
            f"⚠  Còn thiếu {len(missing)} giấy tờ: "
            f"{', '.join(d.loai_giay for d in missing)}"
        )
        warn.setStyleSheet(
            "color:#DC2626;font-size:12px;font-weight:600;border:none;font-family:Arial;"
        )
        warn.setWordWrap(True)
        al.addWidget(warn)
        self._alert_layout.addWidget(alert)

    def _populate(self):
        _clear_doc_layout(self._lay)

        total  = len(self._docs)
        da_nop = sum(1 for d in self._docs if d.da_nop)
        clr    = SUCCESS if da_nop == total and total > 0 else DANGER
        sum_lbl = QLabel(f"Đã nộp: {da_nop}/{total} giấy tờ")
        sum_lbl.setStyleSheet(
            f"color:{clr};font-size:13px;font-weight:700;font-family:Arial;border:none;"
        )
        self._lay.addWidget(sum_lbl)

        if not self._docs:
            no_data = QLabel("Chưa có thông tin giấy tờ")
            no_data.setStyleSheet(
                f"color:#94A3B8;font-size:13px;font-family:Arial;border:none;"
            )
            self._lay.addWidget(no_data)
            self._lay.addStretch()
            return

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
            QTableWidget{background:#FFFFFF;border:none;color:#1E293B;font-size:13px;
                font-family:Arial;gridline-color:#F1F5F9;}
            QTableWidget::item{padding:6px 10px;}
            QTableWidget::item:selected{background:#DBEAFE;color:#1E3A8A;}
            QTableWidget::item:alternate{background:#F8FAFC;}
            QHeaderView::section{background:#F1F5F9;color:#475569;font-size:11px;
                font-weight:700;padding:8px 10px;border:none;border-bottom:2px solid #E2E8F0;}
        """)
        tbl.setColumnWidth(1, 100); tbl.setColumnWidth(2, 100)
        tbl.setColumnWidth(3, 160); tbl.setColumnWidth(4, 150)
        tbl.verticalHeader().setDefaultSectionSize(38)
        tbl.setRowCount(len(self._docs))
        for r, doc in enumerate(self._docs):
            tbl.setItem(r, 0, _doc_tbl_item(doc.loai_giay))
            tt_it = _doc_tbl_item("✓ Đã nộp" if doc.da_nop else "✗ Chưa nộp", center=True, bold=True)
            tt_it.setForeground(QColor(SUCCESS if doc.da_nop else DANGER))
            tbl.setItem(r, 1, tt_it)
            tbl.setItem(r, 2, _doc_tbl_item(fmt_date(doc.ngay_nop) if doc.ngay_nop else "—", center=True))
            tbl.setItem(r, 3, _doc_tbl_item(doc.file_name if doc.has_file else "Chưa có file"))
            tbl.setItem(r, 4, _doc_tbl_item(doc.ghi_chu or ""))
        self._lay.addWidget(tbl)
