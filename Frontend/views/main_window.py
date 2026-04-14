from __future__ import annotations
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from utils.session import Session
from utils.config import PRIMARY, SECONDARY, ACCENT, HIGHLIGHT, TEXT_LIGHT, TEXT_MUTED, BORDER

NAV_ITEMS = [
    ("dashboard", "  Dashboard",   "admin phong_dao_tao giang_vien"),
    ("sinhvien",  "  Sinh viên",   "admin phong_dao_tao"),
    ("hocphan",   "  Học phần",    "admin phong_dao_tao giang_vien"),
    ("diem",      "  Điểm số",     "admin phong_dao_tao giang_vien"),
    ("hocphi",    "  Học phí",     "admin phong_dao_tao"),
    ("baocao",    "  Báo cáo",     "admin phong_dao_tao"),
]


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduStu")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(f"background: {PRIMARY}; color: {TEXT_LIGHT};")
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
        self.stack.setStyleSheet(f"background: {PRIMARY};")
        root.addWidget(self.stack)

    def _make_sidebar(self) -> QFrame:
        sb = QFrame()
        sb.setFixedWidth(200)
        sb.setStyleSheet(f"""
            QFrame {{
                background: {SECONDARY};
                border-right: 1px solid {BORDER};
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
        lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {HIGHLIGHT}; border: none;")
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
        av.setFixedSize(34, 34)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(f"""
            background: {ACCENT};
            color: {TEXT_LIGHT};
            border-radius: 17px;
            font-weight: 700;
            font-size: 13px;
            border: none;
        """)
        name_lbl = QLabel(user.ho_ten if user else "")
        name_lbl.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {TEXT_LIGHT}; border: none;")
        name_lbl.setWordWrap(True)
        av_row.addWidget(av)
        av_row.addWidget(name_lbl, stretch=1)
        ul.addLayout(av_row)

        role_lbl = QLabel(user.role_label if user else "")
        role_lbl.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; border: none; padding-left: 2px;")
        ul.addWidget(role_lbl)

        btn_logout = QPushButton("Đăng xuất")
        btn_logout.setFixedHeight(28)
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUTED};
                border: 1px solid {BORDER};
                border-radius: 5px;
                font-size: 11px;
                margin-top: 4px;
            }}
            QPushButton:hover {{ color: {HIGHLIGHT}; border-color: {HIGHLIGHT}; }}
        """)
        btn_logout.clicked.connect(self._logout)
        ul.addWidget(btn_logout)
        layout.addWidget(user_frame)
        return sb

    def _make_nav_btn(self, key: str, label: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setFixedHeight(42)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setCheckable(True)
        btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding-left: 16px;
                border: none;
                border-left: 3px solid transparent;
                background: transparent;
                font-size: 13px;
                color: {TEXT_MUTED};
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.05);
                color: {TEXT_LIGHT};
            }}
            QPushButton:checked {{
                background: rgba(233,69,96,0.12);
                color: {HIGHLIGHT};
                border-left: 3px solid {HIGHLIGHT};
                font-weight: 600;
            }}
        """)
        btn.clicked.connect(lambda: self._nav_to(key))
        return btn

    def _load_views(self):
        from views.dashboard_view import DashboardView
        from views.student_view   import StudentView
        from views.course_view    import CourseView
        from views.grade_view     import GradeView
        from views.tuition_view   import TuitionView
        from views.report_view    import ReportView

        self._views: dict[str, QWidget] = {
            "dashboard": DashboardView(),
            "sinhvien":  StudentView(),
            "hocphan":   CourseView(),
            "diem":      GradeView(),
            "hocphi":    TuitionView(),
            "baocao":    ReportView(),
        }
        for v in self._views.values():
            self.stack.addWidget(v)

    def _nav_to(self, key: str):
        for k, btn in self._nav_btns.items():
            btn.setChecked(k == key)
        if key in self._views:
            self.stack.setCurrentWidget(self._views[key])
            view = self._views[key]
            if hasattr(view, "refresh"):
                view.refresh()

    def _logout(self):
        reply = QMessageBox.question(
            self, "Đăng xuất", "Bạn có chắc muốn đăng xuất không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            Session.clear()
            self.close()