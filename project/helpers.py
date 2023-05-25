# OPERATING SYSTEM STUFF
import os
import io
import gc

# DATA SCIENCE
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# API STUFF
import xlrd
import requests
import json

# SQL
from sqlalchemy import (
    create_engine,
    text,
    String,
    Integer,
    Float,
    Boolean,
    MetaData,
    Table,
    select,
)
from sqlalchemy.exc import (
    ProgrammingError,
)  # ProgrammingError catches SQL write exceptions
from sqlalchemy.sql import and_

# CONFIGURATION FILES
import config

# VARS -----------------------------------------

# Map between NYC and Zillow categories
mapping = {
    "Single-family home": ["01 ONE FAMILY DWELLINGS"],
    "Multi-family home": [
        "03 THREE FAMILY DWELLINGS",
        "07 RENTALS - WALKUP APARTMENTS",
        "08 RENTALS - ELEVATOR APARTMENTS",
        "14 RENTALS - 4-10 UNIT",
        "15 CONDOS - 2-10 UNIT RESIDENTIAL",
        "16 CONDOS - 2-10 UNIT WITH COMMERCIAL UNIT",
    ],
    "Apartment": [
        "07 RENTALS - WALKUP APARTMENTS",
        "08 RENTALS - ELEVATOR APARTMENTS",
        "09 COOPS - WALKUP APARTMENTS",
        "10 COOPS - ELEVATOR APARTMENTS",
    ],
    "Condo": [
        "04 TAX CLASS 1 CONDOS",
        "12 CONDOS - WALKUP APARTMENTS",
        "13 CONDOS - ELEVATOR APARTMENTS",
    ],
    "Co-op": [
        "09 COOPS - WALKUP APARTMENTS",
        "10 COOPS - ELEVATOR APARTMENTS",
        "17 CONDO COOPS",
    ],
    "Duplex": ["02 TWO FAMILY DWELLINGS"],
    "Townhouse": ["01 ONE FAMILY DWELLINGS", "02 TWO FAMILY DWELLINGS"],
    "Brownstone": ["01 ONE FAMILY DWELLINGS", "02 TWO FAMILY DWELLINGS"],
    "Row house": ["01 ONE FAMILY DWELLINGS", "02 TWO FAMILY DWELLINGS"],
}

intermediary_mapping = {
    "Single-family home": ["01 ONE FAMILY DWELLINGS"],
    "Duplex": ["02 TWO FAMILY DWELLINGS"],
    "Multi-family home": [
        "03 THREE FAMILY DWELLINGS",
        "14 RENTALS - 4-10 UNIT",
        "15 CONDOS - 2-10 UNIT RESIDENTIAL",
        "16 CONDOS - 2-10 UNIT WITH COMMERCIAL UNIT",
    ],
    "Apartment": ["08 RENTALS - ELEVATOR APARTMENTS", "07 RENTALS - WALKUP APARTMENTS"],
    "Condo": [
        "04 TAX CLASS 1 CONDOS",
        "12 CONDOS - WALKUP APARTMENTS",
        "13 CONDOS - ELEVATOR APARTMENTS",
    ],
    "Co-op": [
        "17 CONDO COOPS",
        "09 COOPS - WALKUP APARTMENTS",
        "10 COOPS - ELEVATOR APARTMENTS",
    ],
}


# Outline the columns of the DataFrame that
# will hold our new geocode information
geocoding_data_types_df = {
    "BOROUGH CODE": int,
    "BOROUGH": str,
    "NEIGHBORHOOD": str,
    "ADDRESS": str,
    "LATITUDE": float,
    "LONGITUDE": float,
    "GEOCODING ERR": bool,
}

geocoding_data_types_sqlalchemy = {
    "BOROUGH CODE": Integer,
    "BOROUGH": String(25),
    "NEIGHBORHOOD": String(100),
    "ADDRESS": String(255),
    "LATITUDE": Float,
    "LONGITUDE": Float,
    "GEOCODING ERR": Boolean,
}

# URL order: [Manhattan, Bronx, Brooklyn, Queens, Staten Island]
dataURLs = [
    "https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/"
    "rollingsales_manhattan.xlsx",
    "https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/"
    "rollingsales_bronx.xlsx",
    "https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/"
    "rollingsales_brooklyn.xlsx",
    "https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/"
    "rollingsales_queens.xlsx",
    "https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/"
    "rollingsales_statenisland.xlsx",
]

# FUNCTION DECLARATIONS ------------------------


def geolocate(row):
    """
    Geolocates a row by running a geocoding API request based on the address information provided in the row.

    Args:
        row (pandas.Series): A row containing address information and geocoding status.

    Returns:
        pandas.Series: The updated row with latitude and longitude information if geocoding was successful,
        or with geocoding error flag and null latitude and longitude values if geocoding failed.
    """
    if not row["GEOCODING ERR"]:  # If GEOCODING ERR is False, run the geocoding API
        address = (
            ", ".join(
                [
                    row["ADDRESS"],
                    # row['NEIGHBORHOOD'],
                    row["BOROUGH"],
                ]
            )
            + ", New York City"
        )
        response = requests.get(
            f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={config.GOOGLE_API_KEY}"
        )
        res = response.json()
        if res["results"]:
            location = res["results"][0]
            if location.get("partial_match"):  # Check for partial match
                row["GEOCODING ERR"] = True
                row["LATITUDE"] = None
                row["LONGITUDE"] = None
            else:
                row["LATITUDE"] = location["geometry"]["location"]["lat"]
                row["LONGITUDE"] = location["geometry"]["location"]["lng"]
        else:
            row[
                "GEOCODING ERR"
            ] = True  # Update GEOCODING ERR to True if geolocation failed
            row["LATITUDE"] = None
            row["LONGITUDE"] = None
    return row


def print_sql_table(engine, table_name):
    """
    This function retrieves and prints all the rows from a SQL table.

    Parameters:
    engine (sqlalchemy.engine.Engine): SQLAlchemy engine instance.
    table_name (str): Name of the table in the SQL database to be printed.

    Returns:
    None. The function prints the rows of the SQL table.
    """
    metadata = MetaData()

    # Reflect the table
    table = Table(table_name, metadata, autoload_with=engine)

    # Connect to the engine
    with engine.connect() as connection:
        # Select all rows from the table
        stmt = select([table])
        result = connection.execute(stmt)

        # Print the rows
        for row in result:
            print(row)


"""
# FUN SQLALCHEMY CODE

# Show databases
with engine.connect() as connection:
    result = connection.execute(text("SHOW DATABASES;"))
    databases = [row[0] for row in result]
    print(databases)

# Show tables
with engine.connect() as connection:
    result = connection.execute(text("SHOW TABLES;"))
    tables = [row[0] for row in result]
    print(tables)

# Show all the building classes
This won't work unless the DataFrame 'combined' has been set up
sorted_building_classes = sorted(
    combined["BUILDING CLASS CATEGORY"].unique(),
    key=lambda x: int(x.split(" ")[0])
)

# Show columns from table
with engine.connect() as connection:
    result = connection.execute(text("SHOW COLUMNS FROM geocodes;"))
    tables = [(row[0],row[1]) for row in result]
    print(tables)

# Show data from table
with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM geocodes LIMIT 1;"))
    tables = [(row[0],row[1],row[2],row[3],row[4],row[5],row[6],
               row[7]
              ) for row in result]
    print(tables)

# Verify primary keys
with engine.connect() as connection:
    result = connection.execute(text("SHOW KEYS FROM geocodes;"))
    primary_key_column = result.fetchone()
    if primary_key_column:
        print("Primary key column:", primary_key_column['Column_name'])
    else:
        print("No primary key defined for the table.")
"""


"""
# DATABASE RESETS

# This resets the 'geocodes' table from a .csv in the folder 'project'
# DataFrame: 'geocodes_reset_df'
# SQL Table: 'geocodes'
geocodes_reset_df = pd.read_csv('geocodes_export_backup.csv')
geocodes_reset_df['PRIMARY_KEY'] = geocodes_reset_df['BOROUGH'] + '_' + geocodes_reset_df['ADDRESS']
geocodes_reset_df.to_sql('geocodes', con=engine, index=False, if_exists='replace')

# This resets the 'geocodes' tabke from a .csv in the folder 'project'
# while dropping the last 10 entries...
# DataFrame: 'geocodes_reset_df'
# SQL Table: 'geocodes'

geocodes_reset_df = pd.read_csv('geocodes_export_backup.csv')
geocodes_reset_df.drop(geocodes_reset_df.tail(10).index, inplace=True)
geocodes_reset_df
"""
