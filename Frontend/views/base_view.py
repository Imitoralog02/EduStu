from __future__ import annotations
import math, random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QSize
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient, QBrush, QRadialGradient, QPen
from utils.config import (
    PRIMARY, SECONDARY, ACCENT, TEXT_LIGHT, TEXT_MUTED,
    BORDER, SUCCESS, WARNING, DANGER, INFO, WHITE
)
from utils.helpers import badge_color
from controllers.base import ApiWorker


# ─────────────────────────────────────────────────────────────────────────────
# Particle & AnimatedBackground (shared with LoginView)
# ─────────────────────────────────────────────────────────────────────────────

class _Particle:
    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.reset(initial=True)

    def reset(self, initial=False):
        self.x     = random.uniform(0, self.w)
        self.y     = random.uniform(0, self.h) if initial else self.h + random.uniform(10, 40)
        self.r     = random.uniform(2, 6)
        self.vy    = random.uniform(0.3, 1.1)
        self.vx    = random.uniform(-0.25, 0.25)
        self.alpha = random.uniform(0.15, 0.5)
        self.da    = random.uniform(0.003, 0.007) * random.choice([-1, 1])

    def update(self):
        self.y    -= self.vy
        self.x    += self.vx
        self.alpha += self.da
        if self.alpha > 0.55: self.da = -abs(self.da)
        if self.alpha < 0.08: self.da =  abs(self.da)
        if self.y + self.r < 0 or not (0 <= self.x <= self.w):
            self.reset()


class AnimatedBackground(QWidget):
    """Widget nền động (gradient + glow + particles + stars). Dùng làm base cho các view."""

    def __init__(self):
        super().__init__()
        self._t = 0.0
        self._particles: list[_Particle] = []
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(20)  # 50 fps

    def showEvent(self, e):
        super().showEvent(e)
        if not self._particles:
            w, h = self.width(), self.height()
            self._particles = [_Particle(w, h) for _ in range(55)]

    def _tick(self):
        if not self.isVisible():
            return
        self._t += 0.8
        for pt in self._particles:
            pt.update()
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        pulse = (math.sin(math.radians(self._t * 1.2)) + 1) / 2

        # 1 ── Gradient nền chính
        bg = QLinearGradient(0, 0, w, h)
        bg.setColorAt(0.0,  QColor("#0D1B3E"))
        bg.setColorAt(0.5,  QColor("#1E3A8A"))
        bg.setColorAt(1.0,  QColor("#0D1B3E"))
        p.fillRect(0, 0, w, h, QBrush(bg))

        # 2 ── Glow trung tâm (xanh lam)
        cx, cy = w * 0.3, h * 0.5
        for radius, alpha_base in [(340, 22), (200, 40), (100, 30)]:
            r = radius + pulse * 18
            rg = QRadialGradient(QPointF(cx, cy), r)
            a  = int(alpha_base + pulse * 12)
            rg.setColorAt(0.0, QColor(59, 130, 246, a))
            rg.setColorAt(1.0, QColor(59, 130, 246, 0))
            p.setBrush(QBrush(rg))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # Glow phụ góc phải (vàng nhạt)
        rx, ry = w * 0.85, h * 0.15
        rg2 = QRadialGradient(QPointF(rx, ry), 200)
        rg2.setColorAt(0.0, QColor(251, 191, 36, int(14 + pulse * 8)))
        rg2.setColorAt(1.0, QColor(251, 191, 36, 0))
        p.setBrush(QBrush(rg2))
        p.drawEllipse(QRectF(rx - 200, ry - 200, 400, 400))

        # Glow phụ góc dưới phải (tím)
        rx2, ry2 = w * 0.75, h * 0.85
        rg3 = QRadialGradient(QPointF(rx2, ry2), 180)
        rg3.setColorAt(0.0, QColor(124, 58, 237, int(16 + pulse * 10)))
        rg3.setColorAt(1.0, QColor(124, 58, 237, 0))
        p.setBrush(QBrush(rg3))
        p.drawEllipse(QRectF(rx2 - 180, ry2 - 180, 360, 360))

        # 3 ── Particles
        p.setPen(Qt.PenStyle.NoPen)
        for pt in self._particles:
            rg4 = QRadialGradient(QPointF(pt.x, pt.y), pt.r)
            rg4.setColorAt(0.0, QColor(147, 197, 253, int(pt.alpha * 255)))
            rg4.setColorAt(0.7, QColor(96,  165, 250, int(pt.alpha * 100)))
            rg4.setColorAt(1.0, QColor(59,  130, 246, 0))
            p.setBrush(QBrush(rg4))
            p.drawEllipse(QRectF(pt.x - pt.r, pt.y - pt.r, pt.r * 2, pt.r * 2))

        # 4 ── Sao nhấp nháy
        random.seed(42)
        for _ in range(80):
            sx = random.uniform(0, w)
            sy = random.uniform(0, h)
            sa = random.uniform(0.1, 0.45)
            twinkle = abs(math.sin(math.radians(self._t * random.uniform(1, 3) + sx)))
            p.setBrush(QColor(255, 255, 255, int(sa * twinkle * 255)))
            p.drawEllipse(QRectF(sx - 1, sy - 1, 2, 2))

        p.end()


# ── Table: white card nổi trên nền tối ──────────────────────────────────────
QSS_TABLE = """
QTableWidget {
    background: #FFFFFF;
    border: none;
    border-radius: 0px;
    color: #1E293B;
    font-size: 14px;
    font-family: Arial;
    outline: none;
    gridline-color: #F1F5F9;
}
QTableWidget::item {
    padding: 9px 12px;
    border: none;
    color: #1E293B;
}
QTableWidget::item:selected {
    background: #DBEAFE;
    color: #1E3A8A;
}
QTableWidget::item:alternate {
    background: #F8FAFC;
}
QHeaderView::section {
    background: #F1F5F9;
    color: #475569;
    font-size: 12px;
    font-weight: 700;
    font-family: Arial;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid #E2E8F0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
QScrollBar:vertical {
    background: #F8FAFC;
    width: 7px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #CBD5E1;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #2563EB;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""

# ── Buttons ──────────────────────────────────────────────────────────────────
QSS_BTN_PRIMARY = """
QPushButton {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #2563EB, stop:1 #7C3AED);
    color: #FFFFFF;
    border: none;
    border-radius: 9px;
    font-size: 14px;
    font-weight: 600;
    font-family: Arial;
    padding: 0 20px;
}
QPushButton:hover   { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 #1D4ED8, stop:1 #6D28D9); }
QPushButton:pressed { background: #1E40AF; }
QPushButton:disabled { background: #334155; color: #64748B; }
"""

QSS_BTN_GHOST = f"""
QPushButton {{
    background: rgba(255,255,255,0.08);
    color: {TEXT_MUTED};
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 9px;
    font-size: 14px;
    font-family: Arial;
    padding: 0 16px;
}}
QPushButton:hover   {{
    background: rgba(255,255,255,0.14);
    color: {TEXT_LIGHT};
    border-color: rgba(255,255,255,0.3);
}}
QPushButton:pressed {{ background: rgba(255,255,255,0.2); }}
"""

QSS_BTN_DANGER = """
QPushButton {
    background: rgba(239,68,68,0.12);
    color: #EF4444;
    border: 1px solid rgba(239,68,68,0.35);
    border-radius: 9px;
    font-size: 14px;
    font-family: Arial;
    padding: 0 14px;
}
QPushButton:hover   { background: #EF4444; color: white; border-color: #EF4444; }
QPushButton:pressed { background: #DC2626; }
"""

# ── Inputs ────────────────────────────────────────────────────────────────────
QSS_INPUT = f"""
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {{
    background: rgba(255,255,255,0.08);
    color: {TEXT_LIGHT};
    border: 1.5px solid rgba(255,255,255,0.15);
    border-radius: 9px;
    padding: 0 12px;
    font-size: 14px;
    font-family: Arial;
    height: 38px;
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: #2563EB;
    background: rgba(37,99,235,0.15);
}}
QLineEdit::placeholder {{ color: #64748B; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: #0F2355;
    color: {TEXT_LIGHT};
    border: 1px solid #1E3659;
    font-size: 14px;
    font-family: Arial;
    selection-background-color: #2563EB;
    selection-color: white;
    outline: none;
}}
"""

# ── Dialog / Form helpers ─────────────────────────────────────────────────────
QSS_DIALOG        = "background:#FFFFFF; color:#1E293B; font-family:Arial;"
QSS_SECTION_TITLE = f"color:{TEXT_LIGHT};font-size:15px;font-weight:700;font-family:Arial;"
QSS_LABEL_MUTED   = f"color:{TEXT_MUTED};font-size:13px;font-family:Arial;"
QSS_LABEL_FIELD   = "color:#475569;font-size:13px;font-weight:600;font-family:Arial;"

# ── Input inside white dialogs ────────────────────────────────────────────────
QSS_INPUT_LIGHT = """
QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
    background: #F8FAFC;
    color: #1E293B;
    border: 1.5px solid #E2E8F0;
    border-radius: 9px;
    padding: 0 12px;
    font-size: 14px;
    font-family: Arial;
    height: 38px;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #2563EB;
    background: #EFF6FF;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: #FFFFFF;
    color: #1E293B;
    border: 1px solid #E2E8F0;
    font-size: 14px;
    font-family: Arial;
    selection-background-color: #DBEAFE;
    selection-color: #1E3A8A;
    outline: none;
}
"""


class LoadingOverlay(QWidget):
    """Overlay mờ hiện spinner + text khi đang load data."""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setVisible(False)

        self._angle = 0
        self._spin_timer = QTimer(self)
        self._spin_timer.timeout.connect(self._spin)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._lbl_spinner = QLabel()
        self._lbl_spinner.setFixedSize(56, 56)
        self._lbl_spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._lbl_text = QLabel("Đang tải dữ liệu...")
        self._lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_text.setStyleSheet(
            "color: #FFFFFF; font-size: 14px; font-family: Arial; "
            "font-weight: 600; background: transparent;"
        )

        layout.addWidget(self._lbl_spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(self._lbl_text, alignment=Qt.AlignmentFlag.AlignCenter)

    def _spin(self):
        self._angle = (self._angle + 8) % 360
        self._lbl_spinner.update()
        self.update()

    def show_loading(self, text: str = "Đang tải dữ liệu..."):
        self._lbl_text.setText(text)
        self.resize(self.parent().size())
        self.raise_()
        self.setVisible(True)
        self._spin_timer.start(16)

    def hide_loading(self):
        self._spin_timer.stop()
        self.setVisible(False)

    def resizeEvent(self, e):
        if self.parent():
            self.resize(self.parent().size())
        super().resizeEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Nền mờ
        p.fillRect(0, 0, w, h, QColor(0, 0, 0, 160))

        # Spinner tròn
        cx, cy = w / 2, h / 2 - 20
        r = 22
        pen = QPen(QColor(255, 255, 255, 40), 4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))

        # Arc xoay
        arc_pen = QPen(QColor(96, 165, 250), 4)
        arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(arc_pen)
        p.drawArc(QRectF(cx - r, cy - r, r * 2, r * 2),
                  (-self._angle) * 16, 100 * 16)

        p.end()


def make_card(parent=None, radius: int = 16, shadow_blur: int = 30,
              shadow_alpha: int = 60) -> QFrame:
    """Tạo QFrame card trắng nổi trên nền tối."""
    card = QFrame(parent)
    card.setStyleSheet(f"""
        QFrame {{
            background: #FFFFFF;
            border-radius: {radius}px;
            border: none;
        }}
    """)
    sh = QGraphicsDropShadowEffect(card)
    sh.setBlurRadius(shadow_blur)
    sh.setOffset(0, 6)
    sh.setColor(QColor(0, 0, 0, shadow_alpha))
    card.setGraphicsEffect(sh)
    return card


# ─────────────────────────────────────────────────────────────────────────────
class BaseView(AnimatedBackground):
    PAGE_TITLE = ""
    PAGE_SUB   = ""

    def __init__(self):
        super().__init__()
        self._workers: list[ApiWorker] = []
        self._loading_count = 0
        self.setStyleSheet(f"color: {TEXT_LIGHT}; font-family: Arial;")
        self._build_base()
        self.build_ui()
        self._overlay = LoadingOverlay(self)

    def _build_base(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Header bán trong suốt (title + actions) ──
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("""
            QFrame {
                background: rgba(10, 22, 40, 0.82);
                border-bottom: 1px solid rgba(30, 54, 89, 0.8);
            }
        """)
        hdr_frame.setFixedHeight(72)
        hdr_inner = QHBoxLayout(hdr_frame)
        hdr_inner.setContentsMargins(28, 0, 28, 0)

        lbl_col = QVBoxLayout()
        lbl_col.setSpacing(2)
        self._lbl_title = QLabel(self.PAGE_TITLE)
        self._lbl_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self._lbl_title.setStyleSheet(f"color:{TEXT_LIGHT}; background:transparent;")
        self._lbl_sub = QLabel(self.PAGE_SUB)
        self._lbl_sub.setStyleSheet(
            f"color:{TEXT_MUTED}; font-size:13px; font-family:Arial; background:transparent;"
        )
        lbl_col.addWidget(self._lbl_title)
        lbl_col.addWidget(self._lbl_sub)

        hdr_inner.addLayout(lbl_col)
        hdr_inner.addStretch()
        self._actions_layout = QHBoxLayout()
        self._actions_layout.setSpacing(8)
        hdr_inner.addLayout(self._actions_layout)
        outer.addWidget(hdr_frame)

        # ── Content area ──
        self._content = QWidget()
        self._content.setStyleSheet("background: transparent;")
        self._root = QVBoxLayout(self._content)
        self._root.setContentsMargins(24, 20, 24, 20)
        self._root.setSpacing(14)
        outer.addWidget(self._content)

    def build_ui(self):
        pass

    def refresh(self):
        pass

    # ── Factories ────────────────────────────────────────────────────────────

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
        t.setAlternatingRowColors(True)
        t.setStyleSheet(QSS_TABLE)
        t.verticalHeader().setDefaultSectionSize(42)
        sh = QGraphicsDropShadowEffect(t)
        sh.setBlurRadius(24); sh.setOffset(0, 4)
        sh.setColor(QColor(0, 0, 0, 50))
        t.setGraphicsEffect(sh)
        return t

    def make_table_card(self, columns: list[str]) -> tuple[QFrame, QTableWidget]:
        """Trả về (card_frame, table) — table nằm trong white card."""
        card = make_card(radius=16, shadow_blur=28, shadow_alpha=55)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        t = self.make_table(columns)
        lay.addWidget(t)
        return card, t

    def make_btn(self, text: str, style: str = "ghost") -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(38)
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

    # ── Table helpers ────────────────────────────────────────────────────────

    def cell(self, text: str,
             align=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
             bold=False, color: str | None = None) -> QTableWidgetItem:
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(align)
        if bold:
            item.setFont(QFont("Arial", 14, QFont.Weight.Bold))
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

    # ── Async ────────────────────────────────────────────────────────────────

    def run_async(self, fn, on_success=None, on_error=None,
                  loading_text: str = "Đang tải dữ liệu...") -> ApiWorker:
        self._loading_count += 1
        self._overlay.show_loading(loading_text)

        def _done(result):
            self._loading_count = max(0, self._loading_count - 1)
            if self._loading_count == 0:
                self._overlay.hide_loading()
            if on_success:
                on_success(result)

        def _err(msg: str):
            self._loading_count = max(0, self._loading_count - 1)
            if self._loading_count == 0:
                self._overlay.hide_loading()
            (on_error or self._default_error)(msg)

        w = ApiWorker(fn)
        w.success.connect(_done)
        w.error.connect(_err)
        w.session_expired.connect(self._on_session_expired)
        w.start()
        self._workers.append(w)
        return w

    def _on_session_expired(self):
        self._loading_count = 0
        self._overlay.hide_loading()
        from utils.session import Session
        Session.clear()
        QMessageBox.warning(
            self, "Phiên đăng nhập hết hạn",
            "Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại."
        )
        # Tìm MainWindow và đóng lại để về màn hình login
        top = self.window()
        if top:
            top.close()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, "_overlay"):
            self._overlay.resize(self.size())

    def _default_error(self, msg: str):
        QMessageBox.warning(self, "Lỗi", msg)


# ── Widget phân trang dùng chung ─────────────────────────────────────────────

class PaginationBar(QWidget):
    """
    Thanh phân trang tái sử dụng.

    Cách dùng:
        self._pager = PaginationBar(on_change=self._load)
        self._root.addWidget(self._pager)

    Trong _load():
        page      = self._pager.current_page
        page_size = self._pager.page_size

    Sau khi có data:
        self._pager.update(total=data["total"])
    """

    PAGE_SIZES = [20, 50, 100]

    def __init__(self, on_change, parent=None):
        super().__init__(parent)
        self._on_change   = on_change
        self._current     = 1
        self._total_pages = 1
        self._total_items = 0
        self._build()

    # ── Build UI ─────────────────────────────────────────────────────────

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(6)

        # Tổng số bản ghi
        self._lbl_info = QLabel("")
        self._lbl_info.setStyleSheet("color:#94A3B8;font-size:12px;font-family:Arial;")
        lay.addWidget(self._lbl_info)
        lay.addStretch()

        # Nút trang đầu
        self._btn_first = self._nav_btn("«")
        self._btn_first.clicked.connect(lambda: self._go(1))
        lay.addWidget(self._btn_first)

        # Nút trang trước
        self._btn_prev = self._nav_btn("‹")
        self._btn_prev.clicked.connect(lambda: self._go(self._current - 1))
        lay.addWidget(self._btn_prev)

        # Các nút số trang
        self._page_btns_lay = QHBoxLayout()
        self._page_btns_lay.setSpacing(4)
        lay.addLayout(self._page_btns_lay)

        # Nút trang sau
        self._btn_next = self._nav_btn("›")
        self._btn_next.clicked.connect(lambda: self._go(self._current + 1))
        lay.addWidget(self._btn_next)

        # Nút trang cuối
        self._btn_last = self._nav_btn("»")
        self._btn_last.clicked.connect(lambda: self._go(self._total_pages))
        lay.addWidget(self._btn_last)

        # Chọn số dòng mỗi trang
        sep = QLabel("|")
        sep.setStyleSheet("color:#475569;font-size:13px;")
        lay.addWidget(sep)

        lbl_size = QLabel("Mỗi trang:")
        lbl_size.setStyleSheet("color:#94A3B8;font-size:12px;font-family:Arial;")
        lay.addWidget(lbl_size)

        self._cmb_size = QComboBox()
        self._cmb_size.addItems([str(s) for s in self.PAGE_SIZES])
        self._cmb_size.setFixedSize(70, 28)
        self._cmb_size.setStyleSheet("""
            QComboBox {
                background: rgba(255,255,255,0.08);
                color: #F1F5F9;
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 6px;
                padding: 0 8px;
                font-size: 12px;
                font-family: Arial;
            }
            QComboBox::drop-down { border: none; width: 18px; }
            QComboBox QAbstractItemView {
                background: #0F2355; color: #F1F5F9;
                selection-background-color: #2563EB;
                font-size: 12px;
            }
        """)
        self._cmb_size.currentIndexChanged.connect(self._on_size_change)
        lay.addWidget(self._cmb_size)

        self._refresh_ui()

    # ── Public API ────────────────────────────────────────────────────────

    @property
    def current_page(self) -> int:
        return self._current

    @property
    def page_size(self) -> int:
        return self.PAGE_SIZES[self._cmb_size.currentIndex()]

    def update_total(self, total: int):
        """Gọi sau khi có data từ API để cập nhật số trang."""
        self._total_items = total
        self._total_pages = max(1, -(-total // self.page_size))  # ceil division
        self._current = min(self._current, self._total_pages)
        self._refresh_ui()

    def reset(self):
        """Reset về trang 1 — gọi khi thay đổi bộ lọc."""
        self._current = 1
        self._refresh_ui()

    # ── Internal ──────────────────────────────────────────────────────────

    def _nav_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(28, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.06);
                color: #94A3B8;
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 6px;
                font-size: 13px;
                font-family: Arial;
            }
            QPushButton:hover:enabled { background: #2563EB; color: white; border-color: #2563EB; }
            QPushButton:disabled { color: #334155; border-color: #1E3659; }
        """)
        return btn

    def _page_btn(self, page: int) -> QPushButton:
        btn = QPushButton(str(page))
        btn.setFixedSize(28, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        is_current = page == self._current
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {'#2563EB' if is_current else 'rgba(255,255,255,0.06)'};
                color: {'white' if is_current else '#94A3B8'};
                border: 1px solid {'#2563EB' if is_current else 'rgba(255,255,255,0.12)'};
                border-radius: 6px;
                font-size: 12px;
                font-family: Arial;
                font-weight: {'700' if is_current else '400'};
            }}
            QPushButton:hover:enabled {{ background: #2563EB; color: white; border-color: #2563EB; }}
        """)
        btn.clicked.connect(lambda: self._go(page))
        return btn

    def _go(self, page: int):
        page = max(1, min(page, self._total_pages))
        if page == self._current:
            return
        self._current = page
        self._refresh_ui()
        self._on_change()

    def _on_size_change(self):
        self._current = 1
        self._total_pages = max(1, -(-self._total_items // self.page_size))
        self._refresh_ui()
        self._on_change()

    def _refresh_ui(self):
        # Label thông tin
        if self._total_items > 0:
            start = (self._current - 1) * self.page_size + 1
            end   = min(self._current * self.page_size, self._total_items)
            self._lbl_info.setText(
                f"Hiển thị {start}–{end} / {self._total_items} sinh viên"
            )
        else:
            self._lbl_info.setText("Không có dữ liệu")

        # Enable/disable nút điều hướng
        self._btn_first.setEnabled(self._current > 1)
        self._btn_prev.setEnabled(self._current > 1)
        self._btn_next.setEnabled(self._current < self._total_pages)
        self._btn_last.setEnabled(self._current < self._total_pages)

        # Render nút số trang (hiện tối đa 7 trang, có "…")
        while self._page_btns_lay.count():
            item = self._page_btns_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        pages = self._visible_pages()
        prev_p = None
        for p in pages:
            if prev_p is not None and p - prev_p > 1:
                dot = QLabel("…")
                dot.setStyleSheet("color:#475569;font-size:12px;")
                dot.setFixedWidth(18)
                self._page_btns_lay.addWidget(dot)
            self._page_btns_lay.addWidget(self._page_btn(p))
            prev_p = p

    def _visible_pages(self) -> list[int]:
        """Trả về list số trang cần hiển thị (có thể bỏ qua giữa với …)."""
        n = self._total_pages
        c = self._current
        if n <= 7:
            return list(range(1, n + 1))
        pages = set()
        pages.update([1, 2, n - 1, n])
        pages.update(range(max(1, c - 1), min(n, c + 2)))
        return sorted(pages)
