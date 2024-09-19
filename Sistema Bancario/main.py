import sys
from PyQt6.QtWidgets import QApplication
from windows import LoginWindow
import db

if __name__ == "__main__":
    db.init_db()
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
