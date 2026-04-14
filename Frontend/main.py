import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from utils.config import APP_NAME, PRIMARY


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(f"""
        QToolTip {{
            background: #16213e;
            color: #eaeaea;
            border: 1px solid #2a2a4a;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
        }}
        QMessageBox {{
            background: #1a1a2e;
            color: #eaeaea;
        }}
        QMessageBox QLabel {{
            color: #eaeaea;
        }}
        QMessageBox QPushButton {{
            background: #0f3460;
            color: #eaeaea;
            border: none;
            border-radius: 5px;
            padding: 5px 16px;
            min-width: 70px;
        }}
        QMessageBox QPushButton:hover {{
            background: #1a4a80;
        }}
    """)

    main_win = None

    def on_login_success(user):
        nonlocal main_win
        login_win.close()
        from views.main_window import MainWindow
        main_win = MainWindow()
        main_win.show()

    from views.login_view import LoginView
    login_win = LoginView(on_success=on_login_success)
    login_win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()