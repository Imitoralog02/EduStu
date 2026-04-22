from __future__ import annotations
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QPoint
)
from PyQt6.QtGui import (
    QFont, QColor
)
from controllers.auth import AuthController
from views.base_view import AnimatedBackground


# ─────────────────────────────────────────────────────────────────────────────
# LoginView
# ─────────────────────────────────────────────────────────────────────────────

class LoginView(AnimatedBackground):

    def __init__(self, on_success):
        super().__init__()
        self._on_success = on_success
        self._ctrl = AuthController()
        self.setWindowTitle("EduStu — Đăng nhập")
        self.setFixedSize(920, 600)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._build_left_overlay()
        self._build_card()
        self._animate_in()

    # ── Branding overlay bên trái ────────────────────────────────────────────

    def _build_left_overlay(self):
        lft = QWidget(self)
        lft.setGeometry(0, 0, 440, 600)
        lft.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lft.setStyleSheet("background: transparent;")

        lay = QVBoxLayout(lft)
        lay.setContentsMargins(52, 72, 32, 60)
        lay.setSpacing(0)

        brand = QLabel("EduStu")
        brand.setFont(QFont("Arial", 44, QFont.Weight.Bold))
        brand.setStyleSheet("color: white; background: transparent; letter-spacing: 3px;")

        tagline = QLabel("Nền tảng quản lý\nsinh viên thế hệ mới")
        tagline.setFont(QFont("Arial", 17))
        tagline.setStyleSheet(
            "color: rgba(255,255,255,0.72); background: transparent;"
        )

        lay.addWidget(brand)
        lay.addSpacing(10)
        lay.addWidget(tagline)
        lay.addStretch()

        for icon, text in [
            ("🎓", "Quản lý hồ sơ sinh viên toàn diện"),
            ("📊", "Điểm số & học phí tức thời"),
            ("📋", "Báo cáo thống kê thông minh"),
        ]:
            row = QHBoxLayout()
            row.setSpacing(10)
            ic = QLabel(icon)
            ic.setFixedSize(38, 38)
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ic.setStyleSheet(
                "background: rgba(255,255,255,0.13); border-radius: 19px;"
                "font-size: 17px; color: white;"
            )
            tx = QLabel(text)
            tx.setStyleSheet(
                "color: rgba(255,255,255,0.85); font-size: 14px;"
                "font-family: Arial; background: transparent;"
            )
            row.addWidget(ic)
            row.addWidget(tx)
            row.addStretch()
            lay.addLayout(row)
            lay.addSpacing(14)

        lay.addSpacing(10)
        yr = QLabel("Đại học Công Nghệ Đông Á · 2024–2025")
        yr.setStyleSheet(
            "color: rgba(255,255,255,0.4); font-size: 11px;"
            "font-family: Arial; background: transparent;"
        )
        lay.addWidget(yr)

    # ── Card đăng nhập ───────────────────────────────────────────────────────

    def _build_card(self):
        CARD_W, CARD_H = 390, 510
        card_x = 920 - CARD_W - 50
        card_y = (600 - CARD_H) // 2

        self._card = QFrame(self)
        self._card.setFixedSize(CARD_W, CARD_H)
        self._card_home = QPoint(card_x, card_y)
        self._card.move(self._card_home)
        self._card.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.97);
                border-radius: 22px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self._card)
        shadow.setBlurRadius(60)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 30, 120))
        self._card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(self._card)
        lay.setContentsMargins(38, 32, 38, 32)
        lay.setSpacing(0)

        # header
        top = QHBoxLayout()
        dot = QFrame(); dot.setFixedSize(10, 10)
        dot.setStyleSheet("background:#2563EB; border-radius:5px;")
        logo = QLabel("EduStu")
        logo.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        logo.setStyleSheet("color:#2563EB; background:transparent;")
        top.addWidget(dot); top.addSpacing(6); top.addWidget(logo)
        top.addStretch()
        lay.addLayout(top)
        lay.addSpacing(22)

        # title
        title = QLabel("Chào mừng trở lại 👋")
        title.setFont(QFont("Arial", 21, QFont.Weight.Bold))
        title.setStyleSheet("color:#0F172A; background:transparent;")
        sub = QLabel("Đăng nhập vào hệ thống quản lý sinh viên")
        sub.setStyleSheet(
            "color:#64748B; font-size:13px; font-family:Arial; background:transparent;"
        )
        sub.setWordWrap(True)
        lay.addWidget(title)
        lay.addSpacing(4)
        lay.addWidget(sub)

        lay.addSpacing(20)

        # username
        lbl_u = QLabel("Tên đăng nhập")
        lbl_u.setStyleSheet(
            "color:#475569; font-size:13px; font-weight:600;"
            "font-family:Arial; background:transparent;"
        )
        self.inp_user = self._inp("Nhập tên đăng nhập...")
        lay.addWidget(lbl_u); lay.addSpacing(6); lay.addWidget(self.inp_user)
        lay.addSpacing(16)

        # password
        lbl_p = QLabel("Mật khẩu")
        lbl_p.setStyleSheet(
            "color:#475569; font-size:13px; font-weight:600;"
            "font-family:Arial; background:transparent;"
        )
        self.inp_pass = self._inp("Nhập mật khẩu...", password=True)
        self.inp_pass.returnPressed.connect(self._login)
        lay.addWidget(lbl_p); lay.addSpacing(6); lay.addWidget(self.inp_pass)
        lay.addSpacing(26)

        # button
        self.btn = QPushButton("  Đăng nhập  →")
        self.btn.setFixedHeight(50)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setFont(QFont("Roboto", 15, QFont.Weight.Bold))
        self.btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #2563EB, stop:1 #7C3AED);
                color: white; border: none; border-radius: 14px;
                font-size:15px; font-weight:700; font-family:Arial;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1D4ED8, stop:1 #6D28D9);
            }
            QPushButton:pressed  { background: #1E40AF; }
            QPushButton:disabled { background: #CBD5E1; color: #94A3B8; }
        """)
        self.btn.clicked.connect(self._login)
        lay.addWidget(self.btn)

        # error
        self.lbl_err = QLabel("")
        self.lbl_err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_err.setStyleSheet("""
            color:#DC2626; font-size:13px; font-family:Arial;
            background:#FEF2F2; border:1.5px solid #FCA5A5;
            border-radius:10px; padding:8px 12px;
        """)
        self.lbl_err.setWordWrap(True)
        self.lbl_err.hide()
        lay.addSpacing(10)
        lay.addWidget(self.lbl_err)
        lay.addStretch()

        footer = QLabel("Đại học Công Nghệ Đông Á · 2024–2025")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            "color:#94A3B8; font-size:11px; font-family:Arial; background:transparent;"
        )
        lay.addWidget(footer)

    # ── Input factory ────────────────────────────────────────────────────────

    def _inp(self, placeholder: str, password=False) -> QLineEdit:
        i = QLineEdit()
        i.setPlaceholderText(placeholder)
        i.setFixedHeight(46)
        if password:
            i.setEchoMode(QLineEdit.EchoMode.Password)
        i.setStyleSheet("""
            QLineEdit {
                background:#F8FAFC; color:#1E293B;
                border:2px solid #E2E8F0; border-radius:12px;
                padding:0 14px; font-size:14px; font-family:Arial;
            }
            QLineEdit:focus { border-color:#2563EB; background:#EFF6FF; }
        """)
        return i

    # ── Animation vào ────────────────────────────────────────────────────────

    def _animate_in(self):
        # Dùng setWindowOpacity để không xung đột WA_TranslucentBackground
        self.setWindowOpacity(0.0)

        fade = QPropertyAnimation(self, b"windowOpacity")
        fade.setDuration(600)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        start_pos = self._card_home + QPoint(0, 45)
        self._card.move(start_pos)
        slide = QPropertyAnimation(self._card, b"pos")
        slide.setDuration(750)
        slide.setStartValue(start_pos)
        slide.setEndValue(self._card_home)
        slide.setEasingCurve(QEasingCurve.Type.OutBack)

        grp = QParallelAnimationGroup(self)
        grp.addAnimation(fade)
        grp.addAnimation(slide)
        grp.start()
        self._intro = grp

    # ── Auth ─────────────────────────────────────────────────────────────────

    def _login(self):
        self.lbl_err.hide()
        self.btn.setEnabled(False)
        self.btn.setText("  Đang đăng nhập...")
        self._ctrl.login(
            self.inp_user.text(), self.inp_pass.text(),
            on_success=self._on_ok,
            on_error=self._on_err,
        )

    def _on_ok(self, user):
        out = QPropertyAnimation(self, b"windowOpacity")
        out.setDuration(350)
        out.setStartValue(1.0)
        out.setEndValue(0.0)
        out.setEasingCurve(QEasingCurve.Type.InCubic)
        out.finished.connect(lambda: self._on_success(user))
        out.start()
        self._fade_out = out

    def _on_err(self, msg: str):
        self.btn.setEnabled(True)
        self.btn.setText("  Đăng nhập  →")
        self.lbl_err.setText("⚠  " + (msg or "Sai tài khoản hoặc mật khẩu."))
        self.lbl_err.show()
        # Shake card
        orig = self._card.pos()
        sh = QPropertyAnimation(self._card, b"pos")
        sh.setDuration(360)
        for t, dx in [(0, 0), (0.15, -10), (0.3, 10), (0.45, -7),
                      (0.6, 7), (0.75, -4), (0.9, 4), (1.0, 0)]:
            sh.setKeyValueAt(t, orig + QPoint(dx, 0))
        sh.setEasingCurve(QEasingCurve.Type.Linear)
        sh.start()
        self._shake = sh

    # ── Drag (frameless) ─────────────────────────────────────────────────────

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "_drag"):
            self.move(e.globalPosition().toPoint() - self._drag)
