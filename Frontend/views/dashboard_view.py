from __future__ import annotations
from PyQt6.QtWidgets import (
    QHBoxLayout, QVBoxLayout, QLabel, QFrame, QGridLayout,
    QProgressBar, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from views.base_view import BaseView, make_card
from controllers.report import ReportController
from utils.config import SUCCESS, WARNING, DANGER, INFO, TEXT_MUTED


def _fmt_vnd(amount) -> str:
    try:
        n = int(amount)
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M ₫"
        return f"{n:,} ₫"
    except Exception:
        return "—"


class StatCard(QFrame):
    def __init__(self, label: str, value: str, color: str, icon: str = ""):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background: #FFFFFF;
                border: none;
                border-left: 5px solid {color};
                border-radius: 14px;
            }}
        """)
        sh = QGraphicsDropShadowEffect(self)
        sh.setBlurRadius(22); sh.setOffset(0, 4)
        sh.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(sh)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        if icon:
            ic = QLabel(icon)
            ic.setFixedSize(44, 44)
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ic.setStyleSheet(f"""
                background: {color}22;
                border-radius: 22px;
                font-size: 20px;
                border: none;
            """)
            layout.addWidget(ic)

        text_col = QVBoxLayout()
        text_col.setSpacing(3)
        lbl = QLabel(label)
        lbl.setStyleSheet("color:#64748B;font-size:12px;font-family:Arial;border:none;font-weight:600;")
        self._val = QLabel(value)
        self._val.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        self._val.setStyleSheet(f"color:{color};border:none;")
        text_col.addWidget(lbl)
        text_col.addWidget(self._val)
        layout.addLayout(text_col)
        layout.addStretch()

    def set_value(self, v: str):
        self._val.setText(v)


class ProgressRow(QFrame):
    def __init__(self, label: str, color: str):
        super().__init__()
        self.setStyleSheet("QFrame{background:transparent;border:none;}")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        self._lbl = QLabel(label)
        self._lbl.setFixedWidth(130)
        self._lbl.setStyleSheet("color:#1E293B;font-size:13px;font-family:Arial;border:none;")

        self._bar = QProgressBar()
        self._bar.setFixedHeight(10)
        self._bar.setTextVisible(False)
        self._bar.setRange(0, 100)
        self._bar.setStyleSheet(f"""
            QProgressBar {{ background:#F1F5F9; border-radius:5px; border:none; }}
            QProgressBar::chunk {{ background:{color}; border-radius:5px; }}
        """)

        self._pct = QLabel("0%")
        self._pct.setFixedWidth(42)
        self._pct.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._pct.setStyleSheet(f"color:{color};font-size:13px;font-weight:700;font-family:Arial;border:none;")

        lay.addWidget(self._lbl)
        lay.addWidget(self._bar, stretch=1)
        lay.addWidget(self._pct)

    def set_pct(self, pct: float, label_suffix: str = ""):
        v = int(min(max(pct, 0), 100))
        self._bar.setValue(v)
        self._pct.setText(f"{pct:.1f}%")
        if label_suffix:
            self._lbl.setText(self._lbl.text().split("(")[0].strip() + f" ({label_suffix})")


class DashboardView(BaseView):
    PAGE_TITLE = "Dashboard"
    PAGE_SUB   = "Tổng quan hệ thống"

    def __init__(self):
        self._ctrl = ReportController()
        super().__init__()

    def build_ui(self):
        # ── Row 1: Stat cards ─────────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(12)

        card_defs = [
            ("Tổng sinh viên",   "—", INFO,    "👥"),
            ("Đang học",         "—", SUCCESS, "📚"),
            ("Cảnh báo học vụ",  "—", WARNING, "⚠️"),
            ("Nợ học phí",       "—", DANGER,  "💸"),
        ]
        self._cards: list[StatCard] = []
        for i, (lbl, val, clr, icon) in enumerate(card_defs):
            c = StatCard(lbl, val, clr, icon)
            self._cards.append(c)
            grid.addWidget(c, 0, i)
        self._root.addLayout(grid)

        # ── Row 2: Trạng thái SV + Học phí ───────────────────────────────
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        # Panel trạng thái sinh viên
        sv_card = make_card(radius=14)
        sv_card.setMinimumHeight(180)
        sv_lay = QVBoxLayout(sv_card)
        sv_lay.setContentsMargins(20, 16, 20, 16)
        sv_lay.setSpacing(12)
        t1 = QLabel("Trạng thái sinh viên")
        t1.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        t1.setStyleSheet("color:#0F172A;border:none;")
        sv_lay.addWidget(t1)

        self._pr_dang_hoc  = ProgressRow("Đang học",  SUCCESS)
        self._pr_bao_luu   = ProgressRow("Bảo lưu",   WARNING)
        self._pr_canh_bao  = ProgressRow("Cảnh báo",  DANGER)
        self._pr_thoi_hoc  = ProgressRow("Thôi học",  "#94A3B8")
        for pr in [self._pr_dang_hoc, self._pr_bao_luu, self._pr_canh_bao, self._pr_thoi_hoc]:
            sv_lay.addWidget(pr)
        sv_lay.addStretch()

        # Panel học phí
        hp_card = make_card(radius=14)
        hp_card.setMinimumHeight(180)
        hp_lay = QVBoxLayout(hp_card)
        hp_lay.setContentsMargins(20, 16, 20, 16)
        hp_lay.setSpacing(10)
        t2 = QLabel("Tổng quan học phí")
        t2.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        t2.setStyleSheet("color:#0F172A;border:none;")
        hp_lay.addWidget(t2)

        def _hp_row(label, color):
            f = QFrame()
            f.setStyleSheet(f"QFrame{{background:{color}11;border-radius:8px;border:1px solid {color}33;}}")
            fl = QHBoxLayout(f)
            fl.setContentsMargins(12, 8, 12, 8)
            lbl_w = QLabel(label)
            lbl_w.setStyleSheet(f"color:#475569;font-size:12px;font-family:Arial;border:none;font-weight:600;")
            val_w = QLabel("—")
            val_w.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            val_w.setStyleSheet(f"color:{color};font-size:15px;font-weight:700;font-family:Arial;border:none;")
            fl.addWidget(lbl_w)
            fl.addWidget(val_w, stretch=1)
            return f, val_w

        f1, self._hp_phai_nop = _hp_row("Tổng phải nộp",  "#2563EB")
        f2, self._hp_da_thu   = _hp_row("Đã thu",          SUCCESS)
        f3, self._hp_con_no   = _hp_row("Còn nợ",          DANGER)

        self._hp_bar = QProgressBar()
        self._hp_bar.setFixedHeight(10)
        self._hp_bar.setTextVisible(False)
        self._hp_bar.setRange(0, 100)
        self._hp_bar.setStyleSheet(f"""
            QProgressBar {{ background:#FEE2E2; border-radius:5px; border:none; }}
            QProgressBar::chunk {{ background:{SUCCESS}; border-radius:5px; }}
        """)
        self._hp_pct = QLabel("Thu được: 0%")
        self._hp_pct.setStyleSheet(f"color:{SUCCESS};font-size:12px;font-family:Arial;border:none;")

        hp_lay.addWidget(f1)
        hp_lay.addWidget(f2)
        hp_lay.addWidget(f3)
        hp_lay.addWidget(self._hp_bar)
        hp_lay.addWidget(self._hp_pct)

        row2.addWidget(sv_card, stretch=3)
        row2.addWidget(hp_card, stretch=2)
        self._root.addLayout(row2)

        # ── Row 3: Cảnh báo tập trung (3 cột) ───────────────────────────
        alert_row = QHBoxLayout()
        alert_row.setSpacing(12)

        def _alert_col(title: str, color: str) -> tuple:
            card = make_card(radius=14)
            card.setMinimumHeight(160)
            lay = QVBoxLayout(card)
            lay.setContentsMargins(16, 14, 16, 14)
            lay.setSpacing(6)
            hdr = QHBoxLayout()
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color};font-size:10px;border:none;")
            t_lbl = QLabel(title)
            t_lbl.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            t_lbl.setStyleSheet("color:#0F172A;border:none;")
            hdr.addWidget(dot); hdr.addWidget(t_lbl); hdr.addStretch()
            count_lbl = QLabel("0")
            count_lbl.setStyleSheet(
                f"color:white;background:{color};border-radius:10px;"
                f"font-size:11px;font-weight:700;padding:2px 8px;border:none;"
            )
            hdr.addWidget(count_lbl)
            lay.addLayout(hdr)
            sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color:#E2E8F0;"); lay.addWidget(sep)
            items_lay = QVBoxLayout(); items_lay.setSpacing(4)
            lay.addLayout(items_lay)
            lay.addStretch()
            return card, items_lay, count_lbl

        c1, self._al_hv_lay,  self._al_hv_cnt  = _alert_col("Cảnh báo học vụ",   DANGER)
        c2, self._al_hp_lay,  self._al_hp_cnt  = _alert_col("Học phí quá hạn",   WARNING)
        c3, self._al_gt_lay,  self._al_gt_cnt  = _alert_col("Thiếu giấy tờ",     INFO)
        alert_row.addWidget(c1); alert_row.addWidget(c2); alert_row.addWidget(c3)
        self._root.addLayout(alert_row)

    def refresh(self):
        self.run_async(self._ctrl._svc.get_dashboard, self._render)

    def _render(self, data: dict):
        tong     = data.get("tong_sv", 0) or 1
        dang_hoc = data.get("dang_hoc", 0)
        bao_luu  = data.get("bao_luu", 0)
        canh_bao = data.get("canh_bao_hv", 0)
        thoi_hoc = data.get("thoi_hoc", 0)
        no_hp    = data.get("no_hoc_phi", 0)
        phai_nop = data.get("tong_phai_nop", 0) or 1
        da_thu   = data.get("tong_da_thu", 0)

        # Stat cards
        self._cards[0].set_value(str(data.get("tong_sv", 0)))
        self._cards[1].set_value(str(dang_hoc))
        self._cards[2].set_value(str(canh_bao))
        self._cards[3].set_value(_fmt_vnd(no_hp))

        # Progress bars trạng thái
        self._pr_dang_hoc.set_pct(dang_hoc / tong * 100, str(dang_hoc))
        self._pr_bao_luu.set_pct(bao_luu   / tong * 100, str(bao_luu))
        self._pr_canh_bao.set_pct(canh_bao / tong * 100, str(canh_bao))
        self._pr_thoi_hoc.set_pct(thoi_hoc / tong * 100, str(thoi_hoc))

        # Học phí
        self._hp_phai_nop.setText(_fmt_vnd(phai_nop))
        self._hp_da_thu.setText(_fmt_vnd(da_thu))
        self._hp_con_no.setText(_fmt_vnd(no_hp))
        pct = int(da_thu / phai_nop * 100)
        self._hp_bar.setValue(min(pct, 100))
        self._hp_pct.setText(f"Thu được: {pct}%")

        # Alerts — 3 loại riêng biệt
        alerts = data.get("alerts", [])
        by_type = {"hoc_vu": [], "hoc_phi": [], "giay_to": []}
        for a in alerts:
            loai = a.get("loai", "")
            if loai in by_type:
                by_type[loai].append(a)

        def _fill_col(lay: QVBoxLayout, cnt_lbl, items: list, color: str):
            while lay.count():
                item = lay.takeAt(0)
                if item.widget(): item.widget().deleteLater()
            cnt_lbl.setText(str(len(items)))
            if not items:
                empty = QLabel("Không có")
                empty.setStyleSheet("color:#94A3B8;font-size:12px;font-family:Arial;border:none;")
                lay.addWidget(empty)
                return
            for a in items[:5]:
                row = QFrame()
                row.setStyleSheet(
                    f"QFrame{{background:{color}11;border:1px solid {color}33;border-radius:7px;}}"
                )
                rl = QHBoxLayout(row); rl.setContentsMargins(10, 6, 10, 6); rl.setSpacing(6)
                dot = QLabel("●"); dot.setStyleSheet(f"color:{color};font-size:9px;border:none;")
                lbl = QLabel(a.get("ho_ten", ""))
                lbl.setStyleSheet("color:#1E293B;font-size:12px;font-family:Arial;border:none;font-weight:600;")
                rl.addWidget(dot); rl.addWidget(lbl, stretch=1)
                lay.addWidget(row)

        _fill_col(self._al_hv_lay, self._al_hv_cnt, by_type["hoc_vu"],  DANGER)
        _fill_col(self._al_hp_lay, self._al_hp_cnt, by_type["hoc_phi"], WARNING)
        _fill_col(self._al_gt_lay, self._al_gt_cnt, by_type["giay_to"], INFO)
