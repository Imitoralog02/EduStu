from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from utils.config import (
    PRIMARY, SECONDARY, ACCENT, TEXT_LIGHT, TEXT_MUTED,
    BORDER, SUCCESS, WARNING, DANGER, INFO, WHITE
)
from utils.helpers import badge_color
from controllers.base import ApiWorker


QSS_TABLE = f"""
QTableWidget {{
    background: {SECONDARY};
    border: 1px solid {BORDER};
    border-radius: 8px;
    color: {TEXT_LIGHT};
    font-size: 13px;
    outline: none;
    gridline-color: {BORDER};
}}
QTableWidget::item {{
    padding: 6px 10px;
    border: none;
}}
QTableWidget::item:selected {{
    background: {ACCENT};
    color: {TEXT_LIGHT};
}}
QHeaderView::section {{
    background: {PRIMARY};
    color: {TEXT_MUTED};
    font-size: 11px;
    font-weight: 600;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {BORDER};
}}
QScrollBar:vertical {{
    background: {PRIMARY};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {ACCENT};
    border-radius: 3px;
}}
"""

QSS_BTN_PRIMARY = f"""
QPushButton {{
    background: {ACCENT};
    color: {TEXT_LIGHT};
    border: none;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    padding: 0 16px;
}}
QPushButton:hover   {{ background: #1a4a80; }}
QPushButton:pressed {{ background: #0a2a50; }}
QPushButton:disabled {{ background: {BORDER}; color: {TEXT_MUTED}; }}
"""

QSS_BTN_GHOST = f"""
QPushButton {{
    background: transparent;
    color: {TEXT_MUTED};
    border: 1px solid {BORDER};
    border-radius: 6px;
    font-size: 12px;
    padding: 0 14px;
}}
QPushButton:hover   {{ background: {SECONDARY}; color: {TEXT_LIGHT}; border-color: {TEXT_MUTED}; }}
QPushButton:pressed {{ background: {ACCENT}; }}
"""

QSS_BTN_DANGER = f"""
QPushButton {{
    background: transparent;
    color: {DANGER};
    border: 1px solid {DANGER};
    border-radius: 6px;
    font-size: 12px;
    padding: 0 12px;
}}
QPushButton:hover   {{ background: {DANGER}; color: white; }}
QPushButton:pressed {{ background: #a01010; }}
"""

QSS_INPUT = f"""
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {{
    background: {PRIMARY};
    color: {TEXT_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 0 10px;
    font-size: 13px;
    height: 34px;
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
    border-color: {ACCENT};
}}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {SECONDARY};
    color: {TEXT_LIGHT};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT};
}}
"""


class BaseView(QWidget):
    """
    Base class cho tất cả màn hình chính.
    Cung cấp: tiêu đề, toolbar actions, make_table, make_btn, run_async.
    """
    PAGE_TITLE = ""
    PAGE_SUB   = ""

    def __init__(self):
        super().__init__()
        self._workers: list[ApiWorker] = []
        self.setStyleSheet(f"background: {PRIMARY}; color: {TEXT_LIGHT};")
        self._build_base()
        self.build_ui()

    def _build_base(self):
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(24, 20, 24, 16)
        self._root.setSpacing(14)

        # Header row
        hdr = QHBoxLayout()
        lbl_col = QVBoxLayout()
        self._lbl_title = QLabel(self.PAGE_TITLE)
        self._lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self._lbl_title.setStyleSheet(f"color: {TEXT_LIGHT};")
        self._lbl_sub = QLabel(self.PAGE_SUB)
        self._lbl_sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px;")
        lbl_col.addWidget(self._lbl_title)
        lbl_col.addWidget(self._lbl_sub)
        hdr.addLayout(lbl_col)
        hdr.addStretch()
        self._actions_layout = QHBoxLayout()
        self._actions_layout.setSpacing(8)
        hdr.addLayout(self._actions_layout)
        self._root.addLayout(hdr)

    def build_ui(self):
        """Override trong subclass để thêm widget."""
        pass

    def refresh(self):
        """Override để reload dữ liệu."""
        pass

    # ------------------------------------------------------------------
    # Factory methods
    # ------------------------------------------------------------------

    def make_table(self, columns: list[str]) -> QTableWidget:
        t = QTableWidget()
        t.setColumnCount(len(columns))
        t.setHorizontalHeaderLabels(columns)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        t.verticalHeader().setVisible(False)
        t.horizontalHeader().setStretchLastSection(True)
        t.setShowGrid(True)
        t.setAlternatingRowColors(False)
        t.setStyleSheet(QSS_TABLE)
        t.verticalHeader().setDefaultSectionSize(38)
        return t

    def make_btn(self, text: str, style: str = "ghost") -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(34)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if style == "primary":
            btn.setStyleSheet(QSS_BTN_PRIMARY)
        elif style == "danger":
            btn.setStyleSheet(QSS_BTN_DANGER)
        else:
            btn.setStyleSheet(QSS_BTN_GHOST)
        return btn

    def add_action(self, btn: QPushButton):
        self._actions_layout.addWidget(btn)

    def set_subtitle(self, text: str):
        self._lbl_sub.setText(text)

    # ------------------------------------------------------------------
    # Table helpers
    # ------------------------------------------------------------------

    def cell(self, text: str, align=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
             bold=False, color: str | None = None) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(align)
        if bold:
            f = QFont("Segoe UI", 13, QFont.Weight.Bold)
            item.setFont(f)
        if color:
            item.setForeground(QColor(color))
        return item

    def badge_cell(self, text: str) -> QTableWidgetItem:
        bg, fg = badge_color(text)
        item = QTableWidgetItem(f"  {text}  ")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setBackground(QColor(bg))
        item.setForeground(QColor(fg))
        return item

    # ------------------------------------------------------------------
    # Async helper
    # ------------------------------------------------------------------

    def run_async(self, fn, on_success=None, on_error=None) -> ApiWorker:
        w = ApiWorker(fn)
        if on_success:
            w.success.connect(on_success)
        w.error.connect(on_error or self._default_error)
        w.start()
        self._workers.append(w)
        return w

    def _default_error(self, msg: str):
        QMessageBox.warning(self, "Lỗi", msg)