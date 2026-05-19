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

import os
import json
from PySide6.QtWidgets import QAbstractItemView, QDialog
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QStandardItem, QStandardItemModel


from app.config import SUB_WINDOW_HEIGHT, SUB_WINDOW_WIDTH
from app.apiservices.request_controller import RequestController

class BusinessDetails(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.request_controller = RequestController(api_client=self.api_client, parent=self)
        self.setWindowTitle("Business Details")
        self.resize(SUB_WINDOW_WIDTH, SUB_WINDOW_HEIGHT)
                
        loader = QUiLoader()
        ui_file = QFile(os.path.join(os.path.dirname(__file__), "BusinessDetails.ui"))
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, None)
        ui_file.close()

        self.ui.setModal(True)

        # Connect signals to handlers
        self.ui.closeButton.clicked.connect(self.on_close_clicked)

        self.similar_model = QStandardItemModel()
        self.ui.similarBusinessTable.setModel(self.similar_model)
        self.ui.similarBusinessTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

    # Override exec to show the dialog
    def exec(self):
        return self.ui.exec()
    
    def on_close_clicked(self):
        self.ui.close()
    
    def load(self, business_id):
        self.clear_details()
        self.request_controller.send("GET", f"/api/businesses/{business_id}", self.on_business_fetched, self.on_business_error, None, self.set_status_message)
        
    
    def on_business_fetched(self, status_code, body):
        """Handle successful business details response"""
        results = json.loads(body)[0]
        business = results.get("business", {})
        categories = results.get("categories", [])
        attributes = results.get("attributes", [])
        today_schedule = results.get("today_schedule", {})
        similar_businesses = results.get("similar_businesses", [])
        print(f"Business details fetched successfully: {business}")
        self.ui.businessName.setText(business.get("business_name", ""))
        self.ui.addressLabel.setText(self.format_address(business))
        self.load_hours(today_schedule)
        self.load_categories(categories)
        self.load_attributes(attributes)
        self.load_similar_businesses(similar_businesses)
        self.set_status_message("Business details loaded.")

    def on_business_error(self, error_message):
        """Handle error in fetching business details"""
        self.set_status_message(f"Failed to load business details: {error_message}")

    def clear_details(self):
        self.ui.businessName.setText("")
        self.ui.addressLabel.setText("")
        self.ui.hoursTitle.setText("Today's Hours:")
        self.ui.hoursLabel.setText("")
        self.ui.categoryList.clear()
        self.ui.attributeList.clear()
        self.similar_model.clear()
        self.set_status_message("Loading business details...")

    def format_address(self, business):
        address = business.get("street_address", "")
        city = business.get("city", "")
        state = business.get("state", "")
        zipcode = business.get("zipcode", "")
        return f"{address}, {city}, {state} {zipcode}"

    def load_hours(self, schedule):
        day = schedule.get("day", "").strip()
        open_time = schedule.get("open", "").strip()
        close_time = schedule.get("close", "").strip()
        if not day or not open_time or not close_time:
            self.ui.hoursTitle.setText("Today's Hours:")
            self.ui.hoursLabel.setText("Closed today")
            return
        self.ui.hoursTitle.setText(f"Today's Hours:   {day}")
        self.ui.hoursLabel.setText(f"Opens:      {open_time}\nCloses:     {close_time}")

    def load_categories(self, categories):
        self.ui.categoryList.clear()
        self.ui.categoryList.addItems(categories)

    def load_attributes(self, attributes):
        self.ui.attributeList.clear()
        for attribute in attributes:
            name = attribute.get("attribute_name", "")
            value = attribute.get("value", "")
            self.ui.attributeList.addItem(f"{name} ({value})")

    def load_similar_businesses(self, businesses):
        headers = ["rank", "distance", "business_name", "street_address", "city", "star_rating", "num_tips"]
        headers_pretty = ["Rank", "Distance", "Business Name", "Street Address", "City", "Star Rating", "Number of Tips"]

        self.similar_model.clear()
        self.similar_model.setHorizontalHeaderLabels(headers_pretty)
        for business in businesses:
            row = []
            for header in headers:
                value = business.get(header, "")
                if header == "distance" and value != "":
                    value = f"{float(value):.2f}"
                row.append(QStandardItem(str(value)))
            self.similar_model.appendRow(row)
        self.ui.similarBusinessTable.resizeColumnsToContents()
        self.ui.similarBusinessTable.setColumnWidth(2, 150)
        self.ui.similarBusinessTable.setColumnWidth(3, 190)

    # -----------------------------------------------------------
    # HELPER METHODS    
    def set_status_message(self, message):
        print(message)  # For debugging, print the message to the console
        if hasattr(self.ui, "statusMsg"):
            self.ui.statusMsg.setText(message)
