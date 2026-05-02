from __future__ import annotations
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from utils.session import Session
from utils.config import PRIMARY, SECONDARY, ACCENT, TEXT_LIGHT, TEXT_MUTED, BORDER

NAV_ITEMS = [
    ("dashboard", "  Dashboard",        "admin phongdt giaovien"),
    ("sinhvien",  "  Sinh viên",        "admin phongdt giaovien"),
    ("giayto",    "  Hồ sơ sinh viên",  "admin phongdt"),
    ("hocphi",    "  Học phí",          "admin phongdt"),
    ("baocao",    "  Báo cáo",          "admin phongdt giaovien"),
]


class MainWindow(QMainWindow):

    def __init__(self, on_logout=None):
        super().__init__()
        self._on_logout = on_logout
        self.setWindowTitle("EduStu")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {PRIMARY};
            }}
            QWidget {{
                color: {TEXT_LIGHT};
                font-family: Arial;
            }}
        """)
        self._build()
        self._load_views()
        self._nav_to("dashboard")

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_sidebar())

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent; font-family: Arial;")
        root.addWidget(self.stack)

    def _make_sidebar(self) -> QFrame:
        sb = QFrame()
        sb.setFixedWidth(200)
        sb.setStyleSheet(f"""
            QFrame {{
                background: {SECONDARY};
                border-right: 1px solid {BORDER};
                font-family: Arial;
            }}
        """)
        layout = QVBoxLayout(sb)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Brand
        brand = QFrame()
        brand.setFixedHeight(64)
        brand.setStyleSheet(f"border-bottom: 1px solid {BORDER};")
        bl = QHBoxLayout(brand)
        bl.setContentsMargins(16, 0, 16, 0)
        lbl = QLabel("EduStu")
        lbl.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #93C5FD; border: none; letter-spacing: 2px;")
        bl.addWidget(lbl)
        layout.addWidget(brand)

        layout.addSpacing(8)

        # Nav buttons
        self._nav_btns: dict[str, QPushButton] = {}
        role = Session.role() or ""
        for key, label, allowed in NAV_ITEMS:
            if role not in allowed:
                continue
            btn = self._make_nav_btn(key, label)
            self._nav_btns[key] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # User info
        user = Session.user()
        user_frame = QFrame()
        user_frame.setStyleSheet(f"border-top: 1px solid {BORDER};")
        ul = QVBoxLayout(user_frame)
        ul.setContentsMargins(14, 10, 14, 10)
        ul.setSpacing(4)

        av_row = QHBoxLayout()
        av = QLabel(user.avatar_text if user else "?")
        av.setFixedSize(38, 38)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(f"""
            background: rgba(37,99,235,0.25);
            color: #93C5FD;
            border-radius: 19px;
            font-weight: 700;
            font-size: 15px;
            font-family: Arial;
            border: 1px solid rgba(37,99,235,0.4);
        """)
        name_lbl = QLabel(user.ho_ten if user else "")
        name_lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {TEXT_LIGHT}; border: none; font-family: Arial;")
        name_lbl.setWordWrap(True)
        av_row.addWidget(av)
        av_row.addWidget(name_lbl, stretch=1)
        ul.addLayout(av_row)

        role_lbl = QLabel(user.role_label if user else "")
        role_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_MUTED}; border: none; padding-left: 2px; font-family: Arial;")
        ul.addWidget(role_lbl)

        btn_logout = QPushButton("Đăng xuất")
        btn_logout.setFixedHeight(32)
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet(f"""
            QPushButton {{
                background: rgba(239,68,68,0.1);
                color: #FCA5A5;
                border: 1px solid rgba(239,68,68,0.3);
                border-radius: 7px;
                font-size: 13px;
                font-family: Arial;
                margin-top: 4px;
            }}
            QPushButton:hover {{ background: #EF4444; color: white; border-color: #EF4444; }}
        """)
        btn_logout.clicked.connect(self._logout)
        ul.addWidget(btn_logout)
        layout.addWidget(user_frame)
        return sb

    def _make_nav_btn(self, key: str, label: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setFixedHeight(46)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setCheckable(True)
        btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding-left: 20px;
                border: none;
                border-left: 3px solid transparent;
                background: transparent;
                font-size: 14px;
                font-family: Arial;
                color: {TEXT_MUTED};
            }}
            QPushButton:hover {{
                background: rgba(37,99,235,0.12);
                color: #93C5FD;
                border-left: 3px solid rgba(37,99,235,0.5);
            }}
            QPushButton:checked {{
                background: rgba(37,99,235,0.2);
                color: #BFDBFE;
                border-left: 3px solid {ACCENT};
                font-weight: 700;
            }}
        """)
        btn.clicked.connect(lambda: self._nav_to(key))
        return btn

    def _load_views(self):
        self._views: dict[str, QWidget] = {}
        self._view_factories = {
            "dashboard": lambda: __import__("views.dashboard_view", fromlist=["DashboardView"]).DashboardView(),
            "sinhvien":  lambda: __import__("views.student_view",   fromlist=["StudentView"]).StudentView(),
            "hocphan":   lambda: __import__("views.course_view",    fromlist=["CourseView"]).CourseView(),
            "hocphi":    lambda: __import__("views.tuition_view",   fromlist=["TuitionView"]).TuitionView(),
            "giayto":    lambda: __import__("views.document_view",  fromlist=["DocumentView"]).DocumentView(),
            "baocao":    lambda: __import__("views.report_view",    fromlist=["ReportView"]).ReportView(),
        }

    def _nav_to(self, key: str):
        for k, btn in self._nav_btns.items():
            btn.setChecked(k == key)

        # Tạo view lần đầu khi navigate đến (lazy init)
        if key not in self._views and key in self._view_factories:
            view = self._view_factories[key]()
            self._views[key] = view
            self.stack.addWidget(view)

        if key in self._views:
            view = self._views[key]
            self.stack.setCurrentWidget(view)
            # Chỉ refresh lần đầu (view mới tạo chưa có _loaded)
            if not getattr(view, "_loaded", False):
                if hasattr(view, "refresh"):
                    view.refresh()
                view._loaded = True

    def _logout(self):
        reply = QMessageBox.question(
            self, "Đăng xuất", "Bạn có chắc muốn đăng xuất không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            Session.clear()
            self.close()
            if self._on_logout:
                self._on_logout()