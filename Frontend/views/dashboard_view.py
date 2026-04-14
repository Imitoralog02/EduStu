from __future__ import annotations
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from views.base_view import BaseView
from controllers.report import ReportController
from utils.config import SECONDARY, BORDER, TEXT_LIGHT, TEXT_MUTED, SUCCESS, WARNING, DANGER, INFO, HIGHLIGHT


class StatCard(QFrame):
    def __init__(self, label: str, value: str, color: str):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background: {SECONDARY};
                border: 1px solid {BORDER};
                border-left: 4px solid {color};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; border: none;")
        val = QLabel(value)
        val.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        val.setStyleSheet(f"color: {color}; border: none;")
        layout.addWidget(lbl)
        layout.addWidget(val)
        self._val = val

    def set_value(self, v: str):
        self._val.setText(v)


class DashboardView(BaseView):
    PAGE_TITLE = "Dashboard"
    PAGE_SUB   = "Tổng quan hệ thống"

    def __init__(self):
        self._ctrl = ReportController()
        super().__init__()

    def build_ui(self):
        # Stat cards
        self._grid = QGridLayout()
        self._grid.setSpacing(12)
        colors = [INFO, SUCCESS, WARNING, DANGER]
        labels = ["Tổng sinh viên", "Đang học", "Cảnh báo học vụ", "Nợ học phí"]
        self._cards = []
        for i, (lbl, clr) in enumerate(zip(labels, colors)):
            c = StatCard(lbl, "—", clr)
            self._cards.append(c)
            self._grid.addWidget(c, 0, i)
        self._root.addLayout(self._grid)

        # Alerts panel
        self._alert_frame = QFrame()
        self._alert_frame.setStyleSheet(f"""
            QFrame {{
                background: {SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        al = QVBoxLayout(self._alert_frame)
        al.setContentsMargins(16, 14, 16, 14)
        al.setSpacing(8)
        title = QLabel("Cảnh báo gần đây")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_LIGHT}; border: none;")
        al.addWidget(title)
        self._alert_layout = QVBoxLayout()
        self._alert_layout.setSpacing(6)
        al.addLayout(self._alert_layout)
        self._root.addWidget(self._alert_frame)
        self._root.addStretch()

    def refresh(self):
        self.run_async(self._ctrl._svc.get_dashboard, self._render)

    def _render(self, data: dict):
        vals = [
            str(data.get("tong_sv", 0)),
            str(data.get("dang_hoc", 0)),
            str(data.get("canh_bao_hv", 0)),
            str(data.get("no_hoc_phi", 0)),
        ]
        for card, val in zip(self._cards, vals):
            card.set_value(val)

        while self._alert_layout.count():
            item = self._alert_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        alerts = data.get("alerts", [])
        if not alerts:
            lbl = QLabel("Không có cảnh báo nào.")
            lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; border: none;")
            self._alert_layout.addWidget(lbl)
        for a in alerts[:6]:
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background: rgba(233,69,96,0.1);
                    border-radius: 6px;
                    border: 1px solid rgba(233,69,96,0.3);
                }}
            """)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(10, 6, 10, 6)
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {DANGER}; font-size: 8px; border: none;")
            lbl = QLabel(f"<b>{a.get('ho_ten','')}</b> — {a.get('mo_ta','')}")
            lbl.setStyleSheet(f"color: {TEXT_LIGHT}; font-size: 12px; border: none;")
            rl.addWidget(dot)
            rl.addWidget(lbl)
            self._alert_layout.addWidget(row)