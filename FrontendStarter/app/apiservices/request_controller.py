
# ============================================================
# CS 3431 - Database Systems I
# Worcester Polytechnic Institute (WPI)
# 
# Sakire Arslan Ay
# All rights reserved.
# This code is provided for educational purposes only and may not be used for commercial applications.
# Note: This is starter code provided to students.
#       Modify as instructed in the assignment.
# ============================================================

from PySide6.QtCore import QObject, QThread

from app.apiservices.request_handler import RequestHandler
from app.apiservices import APIClient


class RequestController(QObject):
    def __init__(self, api_client: APIClient, parent) :
        super().__init__(parent)
        self.api_client = api_client
        self.worker_thread: QThread = None
        self.worker: RequestHandler = None

    def send( self, method, endpoint, on_success, on_error, body=None, display_message=None):
        
        if self.worker_thread is not None and self.worker_thread.isRunning():
            if display_message:
                display_message("A request is already running. Please wait.")
            return False

        self.worker = RequestHandler(self.api_client, method, endpoint, body)
        self.worker_thread = QThread(self)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(on_success)
        self.worker.error.connect(on_error)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.cleanup)

        self.worker_thread.start()
        return True

    def cleanup(self):
        if self.worker is not None:
            self.worker.deleteLater()
            self.worker = None
        if self.worker_thread is not None:
            self.worker_thread.deleteLater()
            self.worker_thread = None