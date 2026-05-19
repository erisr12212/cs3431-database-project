Business Finder — CS 3431 Term Project
A back-end and front-end development of an application inspired by Yelp.
Allows users to search and filter through businesses all across the United States. Built as a team project for CS 3431 (Database Systems I) Worcester Polytechnic Institute.

What It Does:
Users can browse and filter businesses through a variety of ways:
Location — filter by U.S. state
Category — search by business type (e.g. breakfast spots, massage parlors, salons)
Price range — filter businesses by cost level
Amenities — filter by features like WiFi availability
Business details — view detailed information about any selected business in a dedicated window

Tech Stack:
LayerTechnologyFrontendJava (Swing)BackendPythonDatabasePostgreSQLQuery LanguageSQL / PL/pgSQL
Project Structure:
FrontendStarter/       # Java frontend (Including UI and business detail window)
BackendStarter/        # Python backend (database connection)
teamlambda_RELATIONS.sql    # Database schema (table definitions)
teamlambda_insertdata.py    # Data insertion script
teamlambda_UPDATE.sql       # Update queries
teamlambda_queries.sql      # Application queries (use cases)
.env.example                # Environment variable template
README.md

Setup:

Prerequisites:
PostgreSQL installed and running
Python 3.x
Java JDK 11+

Steps:

1.
Clone the repository
bashgit clone https://github.com/erisr12212/cs3431-database-project.git
cd cs3431-database-project

2.
Configure environment variables
bashcp .env.example .env
# Edit .env with your PostgreSQL credentials

3.
Create the database schema
bashpsql -U your_username -d your_database -f teamlambda_RELATIONS.sql

4.
Insert sample data
bashpython teamlambda_insertdata.py

5.
Run the application
Open FrontendStarter/ in your Java IDE
Run the main class to launch the UI

Key Features:
Business filtering, dynamic query generation, business detail viewable window, relational database schema, SQL update, and query scripts

Course Info:

Course: CS 3431 — Database Systems I
Institution: Worcester Polytechnic Institute
Term: 2026
Organization: WPI-CS3431-2026D
