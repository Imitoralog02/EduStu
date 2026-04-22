import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from utils.config import APP_NAME, PRIMARY


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setFont(QFont("Roboto", 11))
    app.setStyleSheet(f"""
        QToolTip {{
            background: #1E3A8A;
            color: #F1F5F9;
            border: 1px solid #2563EB;
            border-radius: 6px;
            padding: 5px 10px;
            font-size: 13px;
            font-family: Arial;
        }}
        QMessageBox {{
            background: #0D1B3E;
            color: #F1F5F9;
            font-family: Arial;
        }}
        QMessageBox QLabel {{
            color: #F1F5F9;
            font-size: 14px;
            font-family: Arial;
        }}
        QMessageBox QPushButton {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #2563EB, stop:1 #7C3AED);
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 6px 20px;
            min-width: 80px;
            font-size: 13px;
            font-family: Arial;
        }}
        QMessageBox QPushButton:hover {{ background: #1D4ED8; }}
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