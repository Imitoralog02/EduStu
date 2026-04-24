from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton,
    QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QScrollArea, QCheckBox, QLineEdit,
    QMessageBox, QGraphicsDropShadowEffect, QTextEdit, QDateEdit,
    QDialog, QGridLayout, QComboBox,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
from views.base_view import BaseView, QSS_INPUT, make_card
from controllers.document import DocumentController
from utils.config import SUCCESS, DANGER, WARNING, TEXT_LIGHT, TEXT_MUTED, BORDER, INFO

TONG_GIAY = 6


# ── Card sinh viên thiếu giấy tờ trong banner cảnh báo ───────────────────────
class MissingCard(QFrame):
    def __init__(self, data, on_click):  # data: DocSummary
        super().__init__()
        self._data = data
        self._on_click = on_click
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(52)
        self.setStyleSheet("""
            QFrame {
                background: rgba(239,68,68,0.08);
                border-radius: 7px;
                border: 1px solid rgba(239,68,68,0.25);
            }
            QFrame:hover { background: rgba(239,68,68,0.18); }
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(10)

        icon = QLabel("⚠")
        icon.setStyleSheet(f"color:{DANGER};font-size:14px;font-weight:700;border:none;")
        icon.setFixedWidth(18)
        lay.addWidget(icon)

        info = QVBoxLayout()
        info.setSpacing(1)
        name_lbl = QLabel(f"{data.ho_ten}  <span style='color:#94A3B8;font-size:11px;'>({data.mssv})</span>")
        name_lbl.setTextFormat(Qt.TextFormat.RichText)
        name_lbl.setStyleSheet(f"color:{TEXT_LIGHT};font-size:13px;font-weight:600;font-family:Arial;border:none;")
        sub_lbl = QLabel(f"Lớp: {data.lop or '—'}  ·  Khoa: {data.khoa or '—'}")
        sub_lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-family:Arial;border:none;")
        info.addWidget(name_lbl)
        info.addWidget(sub_lbl)
        lay.addLayout(info, stretch=1)
count_lbl = QLabel(f"Thiếu {data.con_thieu}/{data.tong}")
        count_lbl.setStyleSheet(f"color:{DANGER};font-size:12px;font-weight:700;font-family:Arial;border:none;")
        lay.addWidget(count_lbl)

        btn = QPushButton("Xem →")
        btn.setFixedSize(60, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(239,68,68,0.18); color:{DANGER};
                border: 1px solid rgba(239,68,68,0.4); border-radius:5px;
                font-size:11px; font-weight:700; font-family:Arial;
            }}
            QPushButton:hover {{ background:{DANGER}; color:white; }}
""")
        btn.clicked.connect(lambda: on_click(data.mssv, data))
        lay.addWidget(btn)

    def mousePressEvent(self, _):
        self._on_click(self._data.mssv, self._data)


# ── Card sinh viên trong danh sách trái ──────────────────────────────────────
class StudentRow(QFrame):
    def __init__(self, data, on_click):  # data: DocSummary
        super().__init__()
        self._mssv = data.mssv
        self._on_click = on_click
        self._data = data
        self._build(data)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _build(self, d):
        self.setFixedHeight(66)
        self._apply_style(False)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(8)

        dot = QLabel()
        dot.setFixedSize(10, 10)
        color = SUCCESS if d.hoan_chinh else (WARNING if d.con_thieu <= 2 else DANGER)
        dot.setStyleSheet(f"background:{color};border-radius:5px;border:none;")
        lay.addWidget(dot)

        info = QVBoxLayout()
        info.setSpacing(1)
        name = QLabel(d.ho_ten)
        name.setStyleSheet(f"color:{TEXT_LIGHT};font-size:13px;font-weight:600;font-family:Arial;border:none;")
        name.setWordWrap(False)
        line2 = QLabel(f"{d.mssv} · {d.lop or '—'}")
        line2.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-family:Arial;border:none;")
        line3 = QLabel(d.khoa or "—")
        line3.setStyleSheet(f"color:#4B91F7;font-size:10px;font-family:Arial;border:none;")
        info.addWidget(name)
        info.addWidget(line2)
        info.addWidget(line3)
        lay.addLayout(info, stretch=1)

        pct = QLabel(f"{d.da_nop}/{d.tong}")
        clr = SUCCESS if d.hoan_chinh else DANGER
        pct.setStyleSheet(f"color:{clr};font-size:12px;font-weight:700;font-family:Arial;border:none;")
        lay.addWidget(pct)

    def _apply_style(self, selected: bool):
        if selected:
            self.setStyleSheet("""
QFrame {
                    background: rgba(37,99,235,0.20);
                    border-radius: 8px;
                    border-left: 3px solid #2563EB;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: rgba(255,255,255,0.04);
                    border-radius: 8px;
                    border-left: 3px solid transparent;
                }
                QFrame:hover { background: rgba(255,255,255,0.08); }
            """)

    def set_selected(self, v: bool):
        self._apply_style(v)

    def mousePressEvent(self, _):
        self._on_click(self._mssv, self._data)

    @property
    def mssv(self):
        return self._mssv


# ── View chính ────────────────────────────────────────────────────────────────
class DocumentView(BaseView):
PAGE_TITLE = "Giấy tờ nhân thân"
    PAGE_SUB   = "Quản lý hồ sơ & thông báo thiếu giấy tờ"

    def __init__(self):
        self._ctrl = DocumentController()
        self._selected_mssv: str | None = None
        self._rows: list[StudentRow] = []
        self._all_summary: list[dict] = []
        self._doc_data: list[dict] = []
        super().__init__()

    def build_ui(self):
        # ── Banner cảnh báo (có thể mở rộng) ───────────────────────────────
        self._banner_frame = QFrame()
        self._banner_frame.setVisible(False)
        self._banner_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(239,68,68,0.10);
                border: 1.5px solid rgba(239,68,68,0.35);
                border-radius: 12px;
            }}
        """)
        banner_lay = QVBoxLayout(self._banner_frame)
        banner_lay.setContentsMargins(14, 10, 14, 10)
        banner_lay.setSpacing(6)

        # Header banner
        banner_hdr = QHBoxLayout()
        self._banner_icon = QLabel("⚠️")
        self._banner_icon.setStyleSheet("border:none;font-size:16px;")
        self._banner_title = QLabel("")
        self._banner_title.setStyleSheet(
            f"color:{DANGER};font-size:13px;font-weight:700;font-family:Arial;border:none;"
        )
        self._btn_toggle = QPushButton("▼ Xem chi tiết")
        self._btn_toggle.setFixedHeight(26)
        self._btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_toggle.setStyleSheet(f"""
            QPushButton {{
                background: rgba(239,68,68,0.15); color:{DANGER};
                border: 1px solid rgba(239,68,68,0.3); border-radius:5px;
                font-size:11px; font-family:Arial; padding:0 10px;
            }}
            QPushButton:hover {{ background:{DANGER}; color:white; }}
""")
        self._btn_toggle.clicked.connect(self._toggle_banner_detail)
        banner_hdr.addWidget(self._banner_icon)
        banner_hdr.addWidget(self._banner_title, stretch=1)
        banner_hdr.addWidget(self._btn_toggle)
        banner_lay.addLayout(banner_hdr)

        # Panel chi tiết (ẩn mặc định)
        self._banner_detail = QFrame()
        self._banner_detail.setVisible(False)
        self._banner_detail.setStyleSheet("QFrame{background:transparent;border:none;}")
        self._banner_detail_lay = QVBoxLayout(self._banner_detail)
        self._banner_detail_lay.setContentsMargins(0, 4, 0, 0)
        self._banner_detail_lay.setSpacing(4)
        banner_lay.addWidget(self._banner_detail)

        self._root.addWidget(self._banner_frame)

        # ── Layout chính ─────────────────────────────────────────────────────
        main = QHBoxLayout()
        main.setSpacing(14)

        # ── Cột trái: danh sách sinh viên ────────────────────────────────────
        left = QFrame()
        left.setFixedWidth(270)
left.setStyleSheet("""
            QFrame {
                background: rgba(10,22,40,0.6);
                border-radius: 14px;
                border: 1px solid rgba(255,255,255,0.08);
            }
        """)
        sh = QGraphicsDropShadowEffect(left)
        sh.setBlurRadius(20); sh.setOffset(0, 3)
        sh.setColor(QColor(0, 0, 0, 60))
        left.setGraphicsEffect(sh)

        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(8, 12, 8, 12)
        left_lay.setSpacing(6)

        # Header + count
        hdr = QHBoxLayout()
        hdr.setContentsMargins(4, 0, 4, 0)
        lbl_sv = QLabel("Danh sách sinh viên")
        lbl_sv.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-weight:700;font-family:Arial;border:none;")
        self._lbl_count = QLabel("")
        self._lbl_count.setStyleSheet(f"color:{TEXT_MUTED};font-size:11px;font-family:Arial;border:none;")
        self._lbl_count.setAlignment(Qt.AlignmentFlag.AlignRight)
        hdr.addWidget(lbl_sv)
        hdr.addWidget(self._lbl_count, stretch=1)
        left_lay.addLayout(hdr)

        # Search
        self._inp_search = QLineEdit()
        self._inp_search.setPlaceholderText("Tìm tên hoặc MSSV...")
        self._inp_search.setFixedHeight(30)
        self._inp_search.setStyleSheet(QSS_INPUT)
        self._inp_search.textChanged.connect(self._filter_list)
        left_lay.addWidget(self._inp_search)

        # Lọc theo khoa
        self._cmb_khoa = QComboBox()
        self._cmb_khoa.setFixedHeight(28)
        self._cmb_khoa.addItem("Tất cả khoa")
        self._cmb_khoa.setStyleSheet(QSS_INPUT)
self._cmb_khoa.currentIndexChanged.connect(self._filter_list)
        left_lay.addWidget(self._cmb_khoa)

        # Tab filter
        tab = QHBoxLayout()
        tab.setSpacing(4)
        self._tab_all     = self._tab_btn("Tất cả", True)
        self._tab_missing = self._tab_btn("Thiếu", False)
        self._tab_done    = self._tab_btn("Đủ", False)
        self._tab_all.clicked.connect(lambda: self._set_tab("all"))
        self._tab_missing.clicked.connect(lambda: self._set_tab("missing"))
        self._tab_done.clicked.connect(lambda: self._set_tab("done"))
        for b in [self._tab_all, self._tab_missing, self._tab_done]:
            tab.addWidget(b)
        left_lay.addLayout(tab)
        self._current_tab = "all"

        # Scroll area chứa StudentRow
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}")
        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background:transparent;")
        self._list_lay = QVBoxLayout(self._list_widget)
        self._list_lay.setContentsMargins(0, 0, 0, 0)
        self._list_lay.setSpacing(3)
        self._list_lay.addStretch()
scroll.setWidget(self._list_widget)
        left_lay.addWidget(scroll)
        main.addWidget(left)

        # ── Cột phải: bảng giấy tờ ───────────────────────────────────────────
        right = QVBoxLayout()
        right.setSpacing(10)

        # Header info sinh viên đang chọn
        self._info_card = make_card(radius=12)
        self._info_card.setFixedHeight(80)
        il = QVBoxLayout(self._info_card)
        il.setContentsMargins(18, 10, 18, 10)
        il.setSpacing(3)
        self._lbl_sv_name = QLabel("Chọn sinh viên để xem giấy tờ")
        self._lbl_sv_name.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self._lbl_sv_name.setStyleSheet("color:#0F172A;border:none;")
        self._lbl_sv_meta = QLabel("")
        self._lbl_sv_meta.setStyleSheet("color:#64748B;font-size:12px;font-family:Arial;border:none;")
        self._lbl_sv_stat = QLabel("")
        self._lbl_sv_stat.setStyleSheet("font-size:13px;font-family:Arial;border:none;")
        il.addWidget(self._lbl_sv_name)
        il.addWidget(self._lbl_sv_meta)
        right.addWidget(self._info_card)

        # Bảng giấy tờ
        doc_card = make_card(radius=12)
        dl = QVBoxLayout(doc_card)
        dl.setContentsMargins(0, 0, 0, 0)

        self._doc_table = QTableWidget()
        self._doc_table.setColumnCount(5)
        self._doc_table.setHorizontalHeaderLabels(
["Loại giấy tờ", "Trạng thái", "Ngày nộp", "Ghi chú", "Thao tác"]
        )
        self._doc_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._doc_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._doc_table.verticalHeader().setVisible(False)
        self._doc_table.setAlternatingRowColors(True)
        self._doc_table.horizontalHeader().setStretchLastSection(False)
        self._doc_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._doc_table.setColumnWidth(1, 110)
        self._doc_table.setColumnWidth(2, 100)
        self._doc_table.setColumnWidth(3, 180)
        self._doc_table.setColumnWidth(4, 110)
        self._doc_table.verticalHeader().setDefaultSectionSize(44)
        self._doc_table.setStyleSheet("""
            QTableWidget {
                background:#FFFFFF; border:none; color:#1E293B;
                font-size:13px; font-family:Arial; gridline-color:#F1F5F9;
            }
            QTableWidget::item { padding:6px 10px; }
            QTableWidget::item:selected { background:#DBEAFE; color:#1E3A8A; }
            QTableWidget::item:alternate { background:#F8FAFC; }
            QHeaderView::section {
                background:#F1F5F9; color:#475569; font-size:11px;
                font-weight:700; font-family:Arial; padding:8px 10px;
                border:none; border-bottom:2px solid #E2E8F0;
            }
        """)
dl.addWidget(self._doc_table)
        right.addWidget(doc_card)
        main.addLayout(right, stretch=1)
        self._root.addLayout(main)

    # ── Helpers UI ────────────────────────────────────────────────────────────

    def _tab_btn(self, text: str, active: bool) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(26)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._style_tab(btn, active)
        return btn

    def _style_tab(self, btn: QPushButton, active: bool):
        if active:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:{INFO}; color:white; border:none;
                    border-radius:5px; font-size:11px; font-family:Arial;
                    font-weight:700; padding:0 8px;
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:rgba(255,255,255,0.06); color:{TEXT_MUTED};
                    border:1px solid rgba(255,255,255,0.12); border-radius:5px;
                    font-size:11px; font-family:Arial; padding:0 8px;
                }}
QPushButton:hover {{ color:{TEXT_LIGHT}; }}
            """)

    def _set_tab(self, tab: str):
        self._current_tab = tab
        self._style_tab(self._tab_all,     tab == "all")
        self._style_tab(self._tab_missing, tab == "missing")
        self._style_tab(self._tab_done,    tab == "done")
        self._filter_list()

    def _toggle_banner_detail(self):
        visible = not self._banner_detail.isVisible()
        self._banner_detail.setVisible(visible)
        self._btn_toggle.setText("▲ Thu gọn" if visible else "▼ Xem chi tiết")

    # ── Data loading ──────────────────────────────────────────────────────────

    def refresh(self):
        self.run_async(
            self._ctrl._svc.get_summary,
            self._render_list,
            loading_text="Đang tải danh sách...",
        )

    def _render_list(self, summary: list):
        self._all_summary = summary

        # Cập nhật combo khoa
        khoa_set: list[str] = []
        for s in summary:
            k = s.khoa or ""
            if k and k not in khoa_set:
                khoa_set.append(k)
        khoa_set.sort()

        self._cmb_khoa.blockSignals(True)
        cur_khoa = self._cmb_khoa.currentText()
        self._cmb_khoa.clear()
        self._cmb_khoa.addItem("Tất cả khoa")
        for k in khoa_set:
            self._cmb_khoa.addItem(k)
        idx = self._cmb_khoa.findText(cur_khoa)
        self._cmb_khoa.setCurrentIndex(idx if idx >= 0 else 0)
        self._cmb_khoa.blockSignals(False)

        # Cập nhật banner cảnh báo
        thieu = [s for s in summary if not s.hoan_chinh]
        if thieu:
            self._banner_frame.setVisible(True)
            self._banner_title.setText(
f"Có {len(thieu)} sinh viên chưa nộp đủ giấy tờ — click 'Xem chi tiết' để xem danh sách."
            )
            for i in reversed(range(self._banner_detail_lay.count())):
                w = self._banner_detail_lay.itemAt(i).widget()
                if w:
                    w.setParent(None)
            for sv in thieu:
                card = MissingCard(sv, self._select_student_and_scroll)
                self._banner_detail_lay.addWidget(card)
        else:
            self._banner_frame.setVisible(False)

        self._filter_list()

    def _filter_list(self):
        if not self._all_summary:
            return
        search  = self._inp_search.text().strip().lower()
        khoa_f  = self._cmb_khoa.currentText() if self._cmb_khoa.currentIndex() > 0 else ""

        filtered = []
        for s in self._all_summary:
            if search and search not in s.ho_ten.lower() and search not in s.mssv.lower():
continue
            if khoa_f and (s.khoa or "") != khoa_f:
                continue
            if self._current_tab == "missing" and s.hoan_chinh:
                continue
            if self._current_tab == "done" and not s.hoan_chinh:
                continue
            filtered.append(s)

        thieu_count = sum(1 for s in self._all_summary if not s.hoan_chinh)
        self._lbl_count.setText(f"{thieu_count} thiếu / {len(self._all_summary)}")

        for row in self._rows:
            row.setParent(None)
        self._rows.clear()

        for s in filtered:
            row = StudentRow(s, self._select_student)
            if s["mssv"] == self._selected_mssv:
                row.set_selected(True)
            self._list_lay.insertWidget(self._list_lay.count() - 1, row)
            self._rows.append(row)

    def _select_student_and_scroll(self, mssv: str, data: dict):
        """Được gọi từ banner — chọn SV và cuộn danh sách đến đúng row."""
        # Đóng banner detail
        self._banner_detail.setVisible(False)
        self._btn_toggle.setText("▼ Xem chi tiết")
        # Reset tab về "Tất cả" để chắc chắn SV hiện trong list
        self._set_tab("all")
        # Xóa filter khoa nếu đang lọc khác
        if self._cmb_khoa.currentIndex() > 0:
            khoa_sv = data.get("khoa", "")
            idx = self._cmb_khoa.findText(khoa_sv)
            self._cmb_khoa.setCurrentIndex(idx if idx >= 0 else 0)
        self._select_student(mssv, data)

    def _select_student(self, mssv: str, data: dict):
        self._selected_mssv = mssv
        for row in self._rows:
            row.set_selected(row.mssv == mssv)

        # Header info
        khoa = data.khoa or "—"
        lop  = data.lop  or "—"
        self._lbl_sv_name.setText(data.ho_ten)
        self._lbl_sv_meta.setText(f"MSSV: {mssv}  ·  Lớp: {lop}  ·  Khoa: {khoa}")
        done  = data.da_nop
        total = data.tong
        clr   = SUCCESS if data.hoan_chinh else DANGER
status = "✓  Đầy đủ hồ sơ" if data.hoan_chinh else f"⚠  Còn thiếu {data.con_thieu} giấy tờ"
        self._lbl_sv_name.setStyleSheet(
            f"color:#0F172A;border:none;font-family:Arial;font-size:14px;font-weight:700;"
        )
        # Gắn stat vào info_card bằng cách cập nhật lbl_sv_stat (ẩn trong il)
        self._lbl_sv_stat.setText(
            f"<span style='color:{clr};font-weight:700;font-size:13px;'>{done}/{total} — {status}</span>"
        )
        self._lbl_sv_stat.setTextFormat(Qt.TextFormat.RichText)
        # Thêm stat vào layout nếu chưa có
        info_card_lay = self._info_card.layout()
if self._lbl_sv_stat.parent() is None or self._lbl_sv_stat not in [
            info_card_lay.itemAt(i).widget() for i in range(info_card_lay.count()) if info_card_lay.itemAt(i).widget()
        ]:
            info_card_lay.addWidget(self._lbl_sv_stat)

        self.run_async(
            lambda: self._ctrl._svc.get_docs(mssv),
            self._render_docs,
            loading_text="Đang tải giấy tờ...",
        )

    def _render_docs(self, docs: list):
        self._doc_data = docs
        self._doc_table.setRowCount(len(docs))
        for r, d in enumerate(docs):  # d: StudentDocument
            loai = QTableWidgetItem(d.loai_giay)
            loai.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self._doc_table.setItem(r, 0, loai)

            tt_text = "✓  Đã nộp" if d.da_nop else "✗  Chưa nộp"
            tt_item = QTableWidgetItem(tt_text)
            tt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            tt_item.setForeground(QColor(SUCCESS if d.da_nop else DANGER))
            tt_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self._doc_table.setItem(r, 1, tt_item)

            ngay = QTableWidgetItem(d.ngay_nop or "—")
            ngay.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._doc_table.setItem(r, 2, ngay)

            self._doc_table.setItem(r, 3, QTableWidgetItem(d.ghi_chu or ""))

            w = QWidget()
            hl = QHBoxLayout(w)
            hl.setContentsMargins(4, 4, 4, 4)
            btn = QPushButton("Cập nhật")
            btn.setFixedHeight(28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                f"QPushButton{{background:{INFO};color:white;border:none;"
                f"border-radius:5px;font-size:11px;padding:0 10px;}}"
                f"QPushButton:hover{{background:#1D4ED8;}}"
            )
            btn.clicked.connect(lambda _, doc=d: self._open_update(doc))
            hl.addWidget(btn)
            self._doc_table.setCellWidget(r, 4, w)

    def _open_update(self, doc):  # doc: StudentDocument
        dlg = DocUpdateDialog(doc, on_save=lambda **kw: self._save_doc(doc.id, **kw))
        dlg.exec()
def _save_doc(self, doc_id: int, da_nop: bool, ngay_nop, ghi_chu: str):
        def ok(_):
            if self._selected_mssv:
                self.run_async(
                    lambda: self._ctrl._svc.get_docs(self._selected_mssv),
                    self._render_docs,
                )
            self.run_async(self._ctrl._svc.get_summary, self._render_list)

        self.run_async(
lambda: self._ctrl._svc.update_doc(doc_id, da_nop, ngay_nop, ghi_chu),
            ok,
            loading_text="Đang lưu...",
        )


# ── Dialog cập nhật giấy tờ ───────────────────────────────────────────────────
class DocUpdateDialog(QDialog):
    def __init__(self, doc, on_save):  # doc: StudentDocument
        super().__init__()
        self._doc = doc
        self._on_save = on_save
        self.setWindowTitle(f"Cập nhật — {doc.loai_giay}")
        self.setFixedSize(400, 290)
        self.setStyleSheet("background:#FFFFFF;color:#1E293B;font-family:Arial;")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        title = QLabel(self._doc.loai_giay)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color:#0F172A;")
        root.addWidget(title)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#E2E8F0;")
        root.addWidget(sep)

        grid = QGridLayout(); grid.setSpacing(10)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet("color:#475569;font-size:12px;font-weight:600;")
            return l

        da_nop_val = self._doc.da_nop
        self._chk = QCheckBox("Đã nộp")
        self._chk.setChecked(da_nop_val)
        self._chk.setStyleSheet("color:#1E293B;font-size:13px;")

        self._date = QDateEdit()
        self._date.setCalendarPopup(True)
        self._date.setFixedHeight(34)
        self._date.setEnabled(da_nop_val)
        self._date.setStyleSheet("""
            QDateEdit { background:#F8FAFC; border:1.5px solid #E2E8F0;
                        border-radius:8px; padding:0 10px; font-size:13px; color:#1E293B; }
            QDateEdit:focus { border-color:#2563EB; }
            QDateEdit:disabled { background:#F1F5F9; color:#94A3B8; }
        """)
        if self._doc.ngay_nop:
            parts = self._doc.ngay_nop.split("-")
            try:
                self._date.setDate(QDate(int(parts[0]), int(parts[1]), int(parts[2])))
            except Exception:
                self._date.setDate(QDate.currentDate())
        else:
            self._date.setDate(QDate.currentDate())

        # Toggle date khi check/uncheck
        self._chk.toggled.connect(self._date.setEnabled)
        self._chk.toggled.connect(self._on_check_toggle)

        self._note = QTextEdit()
        self._note.setFixedHeight(56)
self._note.setPlaceholderText("Ghi chú...")
        self._note.setText(self._doc.get("ghi_chu") or "")
self._note.setStyleSheet("""
            QTextEdit { background:#F8FAFC; border:1.5px solid #E2E8F0;
                        border-radius:8px; padding:6px 10px; font-size:13px; color:#1E293B; }
        """)

        grid.addWidget(lbl("Trạng thái"), 0, 0)
        grid.addWidget(self._chk, 0, 1)
        grid.addWidget(lbl("Ngày nộp"), 1, 0)
        grid.addWidget(self._date, 1, 1)
        grid.addWidget(lbl("Ghi chú"), 2, 0)
        grid.addWidget(self._note, 2, 1)
        root.addLayout(grid)
        root.addStretch()

        # Trạng thái hiện tại (hint)
        hint_text = "✓ Đã nộp" if self._doc.da_nop else "✗ Chưa nộp"
        hint_clr  = SUCCESS if self._doc.da_nop else DANGER
        self._hint = QLabel(f"Trạng thái hiện tại: <b style='color:{hint_clr}'>{hint_text}</b>")
        self._hint.setTextFormat(Qt.TextFormat.RichText)
        self._hint.setStyleSheet("font-size:12px;color:#64748B;")
        root.addWidget(self._hint)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        bc = QPushButton("Hủy"); bc.setFixedHeight(34); bc.clicked.connect(self.reject)
        bc.setStyleSheet(
            "QPushButton{background:transparent;color:#475569;border:1px solid #E2E8F0;"
            "border-radius:7px;padding:0 16px;}"
        )
        bs = QPushButton("Lưu"); bs.setFixedHeight(34); bs.clicked.connect(self._save)
        bs.setStyleSheet(
            f"QPushButton{{background:{INFO};color:white;border:none;"
            f"border-radius:7px;font-weight:700;padding:0 20px;}}"
            f"QPushButton:hover{{background:#1D4ED8;}}"
        )
        btn_row.addWidget(bc); btn_row.addWidget(bs)
        root.addLayout(btn_row)

    def _on_check_toggle(self, checked: bool):
        clr  = SUCCESS if checked else DANGER
        text = "✓ Đã nộp" if checked else "✗ Chưa nộp"
        self._hint.setText(f"Trạng thái mới: <b style='color:{clr}'>{text}</b>")

    def _save(self):
        da_nop  = self._chk.isChecked()
        qd      = self._date.date()
        ngay    = f"{qd.year()}-{qd.month():02d}-{qd.day():02d}" if da_nop else None
        ghi_chu = self._note.toPlainText().strip() or None
        self._on_save(da_nop=da_nop, ngay_nop=ngay, ghi_chu=ghi_chu)
        self.accept()