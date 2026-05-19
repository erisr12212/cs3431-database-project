import sys
from PySide6.QtWidgets import QApplication

from app.ui.yelp_app import YelpApp


def run():
    app = QApplication(sys.argv)
    window = YelpApp()
    window.show()
    return app.exec()
