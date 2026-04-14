from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from controllers.auth import AuthController
from utils.config import PRIMARY, SECONDARY, ACCENT, HIGHLIGHT, TEXT_LIGHT, TEXT_MUTED, BORDER, DANGER


class LoginView(QWidget):

    def __init__(self, on_success):
        super().__init__()
        self._on_success = on_success
        self._ctrl = AuthController()
        self.setWindowTitle("EduStu — Đăng nhập")
        self.setFixedSize(420, 520)
        self.setStyleSheet(f"background: {PRIMARY};")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setFixedWidth(340)
        card.setStyleSheet(f"""
            QFrame {{
                background: {SECONDARY};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(32, 36, 32, 32)
        cl.setSpacing(0)

        # Logo
        logo = QLabel("EduStu")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        logo.setStyleSheet(f"color: {HIGHLIGHT}; border: none;")

        sub = QLabel("Hệ thống quản lý sinh viên")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; border: none;")

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {BORDER}; margin: 20px 0 24px 0;")

        # Username
        lbl_u = QLabel("Tên đăng nhập")
        lbl_u.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; border: none; margin-bottom: 4px;")
        self.inp_user = self._inp("Nhập username...")

        sp1 = QLabel()
        sp1.setFixedHeight(12)
        sp1.setStyleSheet("border: none;")

        # Password
        lbl_p = QLabel("Mật khẩu")
        lbl_p.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; border: none; margin-bottom: 4px;")
        self.inp_pass = self._inp("••••••••", password=True)
        self.inp_pass.returnPressed.connect(self._login)

        sp2 = QLabel()
        sp2.setFixedHeight(20)
        sp2.setStyleSheet("border: none;")

        # Button
        self.btn = QPushButton("Đăng nhập")
        self.btn.setFixedHeight(42)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.setStyleSheet(f"""
            QPushButton {{
                background: {HIGHLIGHT};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover   {{ background: #c73050; }}
            QPushButton:pressed {{ background: #a02040; }}
            QPushButton:disabled {{ background: {BORDER}; color: {TEXT_MUTED}; }}
        """)
        self.btn.clicked.connect(self._login)

        # Error label
        self.lbl_err = QLabel("")
        self.lbl_err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_err.setStyleSheet(f"color: {DANGER}; font-size: 12px; border: none;")
        self.lbl_err.setWordWrap(True)
        self.lbl_err.hide()

        for w in [logo, sub, divider, lbl_u, self.inp_user, sp1,
                  lbl_p, self.inp_pass, sp2, self.btn, self.lbl_err]:
            cl.addWidget(w)

        footer = QLabel("Đại học Công Nghệ Đông Á · 2024–2025")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")

        root.addWidget(card)
        root.addSpacing(20)
        root.addWidget(footer)

    def _inp(self, placeholder: str, password=False) -> QLineEdit:
        i = QLineEdit()
        i.setPlaceholderText(placeholder)
        i.setFixedHeight(38)
        if password:
            i.setEchoMode(QLineEdit.EchoMode.Password)
        i.setStyleSheet(f"""
            QLineEdit {{
                background: {PRIMARY};
                color: {TEXT_LIGHT};
                border: 1px solid {BORDER};
                border-radius: 7px;
                padding: 0 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {HIGHLIGHT}; }}
        """)
        return i

    def _login(self):
        self.lbl_err.hide()
        self.btn.setEnabled(False)
        self.btn.setText("Đang đăng nhập...")
        self._ctrl.login(
            self.inp_user.text(),
            self.inp_pass.text(),
            on_success=self._on_ok,
            on_error=self._on_err,
        )

    def _on_ok(self, user):
        self._on_success(user)

    def _on_err(self, msg: str):
        self.btn.setEnabled(True)
        self.btn.setText("Đăng nhập")
        self.lbl_err.setText(msg or "Sai tài khoản hoặc mật khẩu.")
        self.lbl_err.show()