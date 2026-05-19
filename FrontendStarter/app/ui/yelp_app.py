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
import json
import os

from PySide6.QtCore import QFile, QStringListModel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QAbstractItemView, QMainWindow
from PySide6.QtGui import QStandardItemModel, QStandardItem

from app.config import WINDOW_TITLE, MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT
from app.apiservices import APIClient
from app.apiservices.request_controller import RequestController
from app.ui.business_details import BusinessDetails


class YelpApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT)  # Set window size to match your UI design
        self.setWindowTitle(WINDOW_TITLE)

        # Initialize API client and request controller. 
        # APIClient will be used by both the main window and the business details dialog, so we create it here and pass it down.
        self.api_client = APIClient()
        self.request_controller = RequestController(api_client=self.api_client, parent=self)
        self.wifi_request_controller = RequestController(api_client=self.api_client, parent=self)

        loader = QUiLoader()
        ui_file = QFile(os.path.join(os.path.dirname(__file__), "YelpApp.ui"))
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, None)
        ui_file.close()

        # If the loaded UI is a QMainWindow, transfer its central widget
        if isinstance(self.ui, QMainWindow):
            central = self.ui.takeCentralWidget()
            if central:
                self.setCentralWidget(central)
        else:
            self.setCentralWidget(self.ui)

        # Set up results table model
        self.headers = ["business_name", "street_address", "city", "star_rating", "num_tips", "latitude", "longitude", "business_id"]
        self.headers_pretty = ["Business Name", "Street Address", "City", "Star Rating", "Number of Tips", "Latitude", "Longitude", "Business ID"]

        #customize UI elements as needed
        self.ui.categoryList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.attributeList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.statusMsg.setText("Ready...")

        # set Models for the Category and Attribute List
        self.category_model = QStringListModel()
        self.ui.categoryList.setModel(self.category_model)
        self.attribute_model = QStringListModel()
        self.ui.attributeList.setModel(self.attribute_model)

        # set Model for the Business TableView
        self.business_model = QStandardItemModel()
        self.ui.businessTable.setModel(self.business_model)
        
        # Connect signals to handlers
        self.ui.statesList.currentIndexChanged.connect(self.on_state_changed)
        self.ui.citiesList.currentIndexChanged.connect(self.on_city_changed)
        self.ui.searchButton.clicked.connect(self.on_search_clicked)
        
        # Create the business details dialog once and reuse it
        self.business_window = BusinessDetails(self.api_client, parent=self)
        self.ui.businessTable.doubleClicked.connect(self.on_business_double_clicked)
        
        
    # -----------------------------------------------------------
    # HELPER METHODS
    def set_status_message(self, message):
        self.ui.statusMsg.setText(message)

    # -----------------------------------------------------------
    #  OVERRIDE METHODS
    def showEvent(self, event):
        """Override showEvent to trigger initial data loading when the window is first shown"""
        super().showEvent(event)
        # Only fetch once on first show
        if not hasattr(self, '_initial_load_done'):
            self._initial_load_done = True
            self.request_controller.send("GET", "/api/states", self.on_states_fetched, self.on_states_error, None, self.set_status_message)

    def on_states_fetched(self, status_code, body):
        """Handle successful states response"""
        try:
            states = json.loads(body)
            # Populate your state combo box here
            # Assuming the response has a 'states' key with a list of state names
            self.ui.statesList.addItems(states[0]['states'])
            print(f"States loaded: {states}")
        except json.JSONDecodeError:
            print(f"Failed to parse states JSON: {body}")
    
    def on_states_error(self, message):
        """Handle states fetch error"""
        print(f"Error fetching states: {message}")

    def on_state_changed(self, index):
        print("Selected index in STATES combo box:", index)
        #Fetch the cities from /api/cities endpoint using the selected state
        self.request_controller.send("GET", "/api/cities?state={}".format(self.ui.statesList.currentText()),
            self.on_cities_fetched, self.on_cities_error, None, self.set_status_message)
        
    
    #---------------------------------------------------------------------------------
    # Handlers for cities
    def on_cities_fetched(self, status_code, body):
        """Handle successful cities response"""
        try:
            cities = json.loads(body)
            print(cities[0])
            self.ui.citiesList.clear()
            self.ui.citiesList.addItems(cities[0]['cities'])
            self.set_status_message("Cities loaded successfully.")
        except json.JSONDecodeError:
            print(f"Failed to parse cities in JSON {body}")

    def on_cities_error(self, message):
        """Handle cities fetch error"""
        print(f"Error fetching cities: {message}")

    def on_city_changed(self, index):
        print("Selected index in CITIES combo box:", index)
        if index < 0 or not self.ui.citiesList.currentText():
            return
        #Fetch categories and attributes from /api/filters endpoint using the selected state and city
        self.request_controller.send("GET", "/api/filters?state={}&city={}".format(self.ui.statesList.currentText(), self.ui.citiesList.currentText()),
            self.on_filters_fetched, self.on_filters_error, None, self.set_status_message)
    

    #---------------------------------------------------------------------------------
    # Handlers for categories
    def on_wifi_pricerange_fetched(self, status_code, body):
        """Handle successful WiFi and PriceRange response"""
        print(f"WiFi fetched: {body}")
        try:
            data = json.loads(body)
            self.ui.WiFiScroll.clear()
            self.ui.WiFiScroll.addItem("Any")
            self.ui.WiFiScroll.addItems(data[0]['wifi'])
            self.ui.PriceRangeScroll.clear()
            self.ui.PriceRangeScroll.addItem("Any")
            self.ui.PriceRangeScroll.addItems(data[0]['priceRange'])
            self.set_status_message("WiFi and PriceRange Loaded successfully.")
        except json.JSONDecodeError:
            print(f"Failed to parse WiFi and PriceRange JSON: {body}")
            
    def on_wifi_pricerange_error(self, message):
        """Handle WiFi and PriceRange fetch error"""
        print(f"Error fetching WiFi and PriceRange: {message}")
            
    def on_filters_fetched(self, status_code, body):
        """Handle successful categories response"""
        try: 
            filters = json.loads(body)
            # Populate your category listview here
            # Assuming the response has a 'categories' key with a list of category names
            self.category_model.setStringList(filters[0]['categories'])
            self.set_status_message("Categories Loaded successfully.")
            #load the attributes
            self.attribute_model.setStringList(filters[0]['attributes'])
            self.set_status_message("Attributes Loaded successfully.")
            # Now send the wifi request since filters is done
            self.wifi_request_controller.send("GET", "/api/wifi-pricerange?state={}&city={}".format(self.ui.statesList.currentText(), self.ui.citiesList.currentText()),
                self.on_wifi_pricerange_fetched, self.on_wifi_pricerange_error, None, self.set_status_message)
        except json.JSONDecodeError:
            print(f"Failed to parse categories JSON: {body}")

    def on_filters_error(self, message):
        """Handle attributes fetch error"""
        print(f"Error fetching attributes: {message}")

    #---------------------------------------------------------------------------------
        # Handlers for business search
    def on_search_clicked(self):
    # Gather selected filters and send search request to /api/search endpoint
        selected_categories = [cat.data() for cat in self.ui.categoryList.selectedIndexes()]
        selected_attributes = [atr.data() for atr in self.ui.attributeList.selectedIndexes()]
        selected_wifi = self.ui.WiFiScroll.currentText()
        selected_pricerange = self.ui.PriceRangeScroll.currentText()

        search_body = {
            "state": self.ui.statesList.currentText(),
            "city": self.ui.citiesList.currentText(),
            "categories": selected_categories,
            "attributes": selected_attributes,
            "wifi": selected_wifi if selected_wifi not in ("Any", "") else None,
            "priceRange": selected_pricerange if selected_pricerange not in ("Any", "") else None
        }
        print(f"Search POST request body: {search_body}")
        self.request_controller.send("POST", "/api/businesses", self.on_search_results, self.on_search_error, search_body)

    def on_search_results(self, status_code, body):
        """Handle successful search response"""
        try:
            results = json.loads(body)
            self.update_business_table(results)
        except json.JSONDecodeError:
            print(f"Failed to parse search results JSON: {body}")

    # Helper method to update the business table with search results
    def update_business_table(self, search_results):
        """Update the tableView with business search results."""
        self.business_model.clear()

        if not search_results:
            self.set_status_message("No results found.")
            return

        businesses = search_results[0].get('businesses', [])
        self.business_model.setHorizontalHeaderLabels(self.headers_pretty)

        for row_data in businesses:
            row = [QStandardItem(str(row_data.get(col, ""))) for col in self.headers]
            self.business_model.appendRow(row)
        # Configures tableView
        self.configure_results_table() 
        
        self.set_status_message(f"Found {len(businesses)} businesses.")

    def on_search_error(self, message):
        """Handle search error"""
        self.set_status_message(f"Search failed: {message}")
        print(f"Error performing search: {message}")
        
    def configure_results_table(self):
        """Configure the tableView"""
        id_col = self.headers.index("business_id")
        id_address = self.headers.index("street_address")
        id_name = self.headers.index("business_name")
        self.ui.businessTable.resizeColumnsToContents()
        self.ui.businessTable.setColumnWidth(id_address, min(200, int(self.ui.businessTable.columnWidth(id_address) * 0.9)))
        self.ui.businessTable.setColumnWidth(id_name, min(200, int(self.ui.businessTable.columnWidth(id_name) * 0.9)))
        self.ui.businessTable.hideColumn(id_col)  # hide business_id. We need to keep business_id to get the selected business.
        self.ui.businessTable.setSelectionBehavior(QAbstractItemView.SelectRows)    # select whole rows
        self.ui.businessTable.setSelectionMode(QAbstractItemView.SingleSelection)   # one row at a time
        self.ui.businessTable.setEditTriggers(QAbstractItemView.NoEditTriggers)  # make the table read-only
        self.ui.businessTable.horizontalHeader().setStretchLastSection(True)

        #---------------------------------------------------------------------------------
        # Handlers for business details
    
    def on_business_double_clicked(self, index):
        row = index.row()
        model = self.ui.businessTable.model()
        business_id = model.index(row, self.headers.index("business_id")).data()
        # update business details in the business details dialog and show it modally
        self.business_window.load(business_id)
        self.business_window.exec()  # show modally