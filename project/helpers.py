# OPERATING SYSTEM STUFF
import os
import io
import gc
import time

# CONFIG
import importlib
import config

importlib.reload(config)
username = config.DB_USERNAME
password = config.DB_PASSWORD
hostname = config.DB_HOSTNAME
database_name = config.DB_NAME

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
    # OperationalError,
)
from sqlalchemy.exc import (
    ProgrammingError,
)  # ProgrammingError catches SQL write exceptions
from sqlalchemy.sql import and_

# CONFIGURATION FILES
import config

# VARS -----------------------------------------

# Map between NYC and Zillow categories
"""
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
"""

category_mapping = {
    "01 ONE FAMILY DWELLINGS": "Single-family home",
    "02 TWO FAMILY DWELLINGS": "Duplex",
    "03 THREE FAMILY DWELLINGS": "Multi-family home",
    "14 RENTALS - 4-10 UNIT": "Multi-family home",
    "15 CONDOS - 2-10 UNIT RESIDENTIAL": "Multi-family home",
    "16 CONDOS - 2-10 UNIT WITH COMMERCIAL UNIT": "Multi-family home",
    "08 RENTALS - ELEVATOR APARTMENTS": "Apartment",
    "07 RENTALS - WALKUP APARTMENTS": "Apartment",
    "04 TAX CLASS 1 CONDOS": "Condo",
    "12 CONDOS - WALKUP APARTMENTS": "Condo",
    "13 CONDOS - ELEVATOR APARTMENTS": "Condo",
    "17 CONDO COOPS": "Co-op",
    "09 COOPS - WALKUP APARTMENTS": "Co-op",
    "10 COOPS - ELEVATOR APARTMENTS": "Co-op",
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


def testFunction(toPrint):
    print(f"Printing:{toPrint}")


# Takes in an array of dataframes with the same columns, and returns
# a larger dataframe of the data, combined.
def combineHousingDataSets(dataFrames):
    """
    Combines multiple housing datasets into a single DataFrame.

    Parameters:
    dataFrames (list): A list of pandas DataFrames containing housing data.

    Returns:
    - 'False' if all the required columns are not present in each of
    the dataFrames individually.
    - pandas.DataFrame, a combined DataFrame containing data from all input
    DataFrames if the required columns are present.
    """
    # Define required columns
    REQUIRED_PREPROCESSING_COLUMNS = [
        "BOROUGH",
        "NEIGHBORHOOD",
        "BUILDING CLASS CATEGORY",
        "ADDRESS",
        "LAND SQUARE FEET",
        "GROSS SQUARE FEET",
        "SALE PRICE",
    ]

    # Check to see if columns exist
    for dataFrame in dataFrames:
        # Removes extra spaces
        dataFrame.columns = dataFrame.columns.str.strip()

        # Checks if required columns are present
        for dataFrame in dataFrames:
            if not set(REQUIRED_PREPROCESSING_COLUMNS).issubset(dataFrame.columns):
                # Returns false if they are not
                print(dataFrame)
                return False

    # Combine the dataframes and return a new DataFrame
    return pd.concat(dataFrames, ignore_index=True)


# Remove outliars in the data
def filterOutliers(
    df: pd.DataFrame, thresholds: dict, quantile_lower: float, quantile_upper: float
) -> pd.DataFrame:
    """
    Removes rows with values "close to zero" and outliers from the given DataFrame based on the provided thresholds
    and quantiles.

    Parameters:
    df (pd.DataFrame): The input DataFrame to be cleaned.
    thresholds (dict): A dictionary mapping column names to thresholds. Rows in the columns specified where the value
                       is less than the threshold will be removed.
    quantile_lower (float): The lower quantile for calculating the interquartile range (IQR). This is used to determine
                            the lower bound for outliers.
    quantile_upper (float): The upper quantile for calculating the IQR. This is used to determine the upper bound for
                            outliers.

    Returns:
    pd.DataFrame: A new DataFrame with the outliers and values close to zero removed.

    Raises:
    ValueError: If a column specified in thresholds does not exist in the DataFrame or if it does not contain numeric data.
    """
    # Start by copying the data
    data_clean = df.copy()

    # Validate columns and datatypes
    for col in thresholds:
        if col not in data_clean.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")
        if not pd.api.types.is_numeric_dtype(data_clean[col]):
            raise ValueError(f"Column '{col}' must contain numeric data.")

    # Remove rows with values "close to zero"
    for col, threshold in thresholds.items():
        data_clean = data_clean[data_clean[col] >= threshold]

    # List of columns to remove outliers from
    cols_to_check = list(thresholds.keys())

    # Remove outliers
    for col in cols_to_check:
        # Calculate the IQR of each column
        Q1 = data_clean[col].quantile(quantile_lower)
        Q3 = data_clean[col].quantile(quantile_upper)
        IQR = Q3 - Q1

        # Define the upper and lower bounds for outliers
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Remove outliers
        data_clean = data_clean[
            (data_clean[col] >= lower_bound) & (data_clean[col] <= upper_bound)
        ]

    # Return the cleaned data
    return data_clean


# Checks for missing rows
def check_missing_rows(local_df, sql_table_name, engine):
    """
    Compares a local DataFrame with an SQL table to identify and return any missing rows.

    Args:
    local_df (pandas.DataFrame): The DataFrame to be compared with the SQL table.
    sql_table_name (str): The name of the SQL table to be compared with the local DataFrame.
    engine: The SQLAlchemy engine instance facilitating the database connection.

    Returns:
    pandas.DataFrame or bool: Returns a DataFrame containing missing rows if any are found.
    If no missing rows are detected, returns False.

    Raises:
    KeyError: If mandatory columns are missing in either the local DataFrame or the SQL table DataFrame.
    IOError: If an error arises while executing the SQL query.
    ValueError: If one of the following conditions are encountered:
    - The SQL query yields an empty DataFrame.
    - The local DataFrame is empty.
    - The 'PRIMARY_KEY' column is absent in either the local DataFrame or the SQL table DataFrame.
    """
    try:
        # Create a DataFrame of geo-columns only from local data
        geocodes_local = local_df[
            ["BOROUGH CODE", "BOROUGH", "NEIGHBORHOOD", "ADDRESS"]
        ].copy()

        # Add primary key column
        geocodes_local["PRIMARY_KEY"] = (
            geocodes_local["BOROUGH"] + "_" + geocodes_local["ADDRESS"]
        )

        # Add additional geo-columns for geocoding
        (
            geocodes_local["LATITUDE"],
            geocodes_local["LONGITUDE"],
            geocodes_local["GEOCODING ERR"],
        ) = (None, None, False)

    except KeyError:
        # Error 1: If mandatory columns are missing in the local DataFrame
        raise KeyError(f"Columns are missing in local Dataframe")

    try:
        # Load geocodes SQL table into a DataFrame
        geocodes_table_response = pd.read_sql_query(
            f"SELECT * FROM {sql_table_name}", engine
        )
    except Exception as e:
        # Error 2: If an error occurs while executing the SQL query
        raise IOError(f"SQL query error: {e}")

    if geocodes_table_response.empty:
        raise ValueError("SQL Database is empty")
    expected_columns = [
        "BOROUGH CODE",
        "BOROUGH",
        "NEIGHBORHOOD",
        "ADDRESS",
        "LATITUDE",
        "LONGITUDE",
        "GEOCODING ERR",
        "PRIMARY_KEY",
    ]
    missing_columns = set(expected_columns) - set(geocodes_table_response.columns)
    if missing_columns:
        # Error 3: If the SQL query returns data with the incorrect columns
        raise KeyError("Columns are missing in SQL response")

    if geocodes_local.empty:
        # Error 4: If the local DataFrame is empty
        raise ValueError("Local DataFrame is empty")

    # Error 5: If 'PRIMARY_KEY' column is missing in either of the DataFrames
    if (
        "PRIMARY_KEY" not in geocodes_local.columns
        or "PRIMARY_KEY" not in geocodes_table_response.columns
    ):
        raise ValueError("Missing 'PRIMARY_KEY' column in one of the DataFrames")

    # Find rows in local data not in our existing geocoding data
    missing_rows = geocodes_local[
        ~geocodes_local["PRIMARY_KEY"].isin(geocodes_table_response["PRIMARY_KEY"])
    ].reset_index(drop=True)

    # If there are no missing rows, return False
    if missing_rows.empty:
        print("No missing rows found")
        return False

    # If all criteria are met, return the missing rows
    return missing_rows


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


def connect_to_database(
    username, password, hostname, max_retries=10, retry_interval=10
):
    """
    Attempt to establish a connection to the MySQL database.
    :param username: MySQL username
    :param password: MySQL password
    :param hostname: MySQL host
    :param max_retries: Maximum number of connection attempts
    :param retry_interval: Interval (in seconds) between connection attempts
    :return: SQLAlchemy engine instance if successful, otherwise None
    """
    retry_count = 0
    while retry_count <= max_retries:
        try:
            engine = create_engine(f"mysql+pymysql://{username}:{password}@{hostname}")
            print("Database connection established successfully.")
            return engine
        except Exception as e:
            if "Connection refused" in str(e):
                retry_count += 1
                print(
                    f"Connection attempt {retry_count} failed. Retrying in {retry_interval} seconds..."
                )
                time.sleep(retry_interval)
            else:
                raise  # OperationalError
    print("Max retries reached. Unable to establish a database connection.")
    return None


def create_database(engine, database_name):
    """
    Create a new database, if it doesn't already exist.

    :param engine: SQLAlchemy engine instance
    :param database_name: Name of the database to create
    :return: SQLAlchemy engine instance connected to the new database
    """
    try:
        with engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE {database_name};"))
            print("Database created successfully.")
    except ProgrammingError:
        pass  # Database already exists
    return create_engine(
        f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}"
    )


def silence_warnings():
    """
    Silence SQLAlchemy warnings.
    """
    os.environ["SQLALCHEMY_WARN_20"] = "0"
    os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"
    print("SQLAlchemy warnings silenced.")


def create_table_from_csv(engine, table_name, csv_file, if_exists="fail"):
    """
    Create a new SQL table from a CSV file, if the table doesn't already exist.

    :param engine: SQLAlchemy engine instance
    :param table_name: Name of the table to create
    :param csv_file: Path to the CSV file
    :param if_exists: Behavior when the table already exists. Options are 'fail', 'replace', or 'append'.
                      'fail': If table exists, do nothing.
                      'replace': If table exists, drop it, recreate it, and insert data.
                      'append': If table exists, insert data. Create if does not exist.
                      Default is 'fail'.
    """
    with engine.connect() as connection:
        df = pd.read_csv(csv_file)
        try:
            df.to_sql(table_name, con=engine, index=False, if_exists=if_exists)
        except ValueError:
            print(f"Table {table_name} already exists")
        if if_exists == "fail":
            print(
                f"Table '{table_name}' created from csv '{csv_file}' successfully, or already exists."
            )
        elif if_exists == "replace":
            print(
                f"Table '{table_name}' created or replaced from csv '{csv_file}' successfully."
            )
        elif if_exists == "append":
            print(
                f"Table '{table_name}' created or appended with data from csv '{csv_file}' successfully."
            )
        else:
            print(
                f"Unknown 'if_exists' parameter value. Table '{table_name}' may or may not have been affected."
            )


def add_primary_key(engine, table_name, pk_name):
    """
    Add a new primary key column to a SQL table, if it doesn't already exist.

    :param engine: SQLAlchemy engine instance
    :param table_name: Name of the SQL table
    :param pk_name: Name of the primary key column
    """
    with engine.connect() as connection:
        try:
            connection.execute(
                text(f"ALTER TABLE {table_name} ADD COLUMN {pk_name} VARCHAR(255)")
            )
            print(f"Column {pk_name} created in table {table_name}.")
        except:
            print(f"Column {pk_name} already exists in table {table_name}.")


def set_primary_key(engine, table_name, pk_name, concat_fields):
    """
    Set the values of the primary key column by concatenating fields.

    :param engine: SQLAlchemy engine instance
    :param table_name: Name of the SQL table
    :param pk_name: Name of the primary key column
    :param concat_fields: Fields to concatenate (in SQL format)
    """
    with engine.connect() as connection:
        try:
            connection.execute(
                text(f"UPDATE {table_name} SET {pk_name} = CONCAT({concat_fields})")
            )
            print(f"{pk_name} column values set in table {table_name}.")
        except:
            print(f"{pk_name} column values set error in table {table_name}.")


def create_mapping_table(engine, mapping, table_name="cat_map"):
    """
    Create a new SQL table from a dictionary mapping between NYC
    and ZILLOW housing categories, replacing the table if it
    already exists.

    :param engine: SQLAlchemy engine instance
    :param mapping: Mapping dictionary
    :param table_name: Name of the table to create
    """
    mapping_list = [(k, v) for k, vals in mapping.items() for v in vals]
    mapping_df = pd.DataFrame(
        mapping_list, columns=["ZILLOW CATEGORY", "BUILDING CLASS CATEGORY"]
    )
    with engine.connect() as connection:
        mapping_df.to_sql(table_name, con=engine, index=False, if_exists="replace")
        print(f"Table '{table_name}' created successfully.")
