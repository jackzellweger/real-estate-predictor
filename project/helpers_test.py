# --------------------------------------------------------
# TEST: Create database connections
# --------------------------------------------------------
"""
import config  # for SQL credentials
import time
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
import os

# Testing imports
from unittest.mock import patch


@patch("sqlalchemy.create_engine")
@patch("time.sleep", return_value=None)  # this is to skip the actual sleep
def test_connect_to_database(mock_create_engine, mock_sleep):
    # Silence errors
    os.environ["SQLALCHEMY_WARN_20"] = "0"
    os.environ["SQLALCHEMY_SILENCE_UBER_WARNING"] = "1"

    # Database params & credentials
    username = config.DB_USERNAME
    password = config.DB_PASSWORD
    hostname = config.DB_HOSTNAME
    database_name = "test_database_1"

    mock_create_engine.side_effect = Exception(
        "Connection refused"
    )  # forcing exception

    engine = helpers.connect_to_database(
        username, password, hostname, max_retries=2, retry_interval=1
    )

    # Verifying the retries occurred as expected
    # assert mock_create_engine.call_count == 3  # original call + 2 retries

    # Asserting that None is returned after max retries
    assert engine is None
"""

# --------------------------------------------------------
# TEST: combineHousingDataSets()
# --------------------------------------------------------
import helpers
import pandas as pd
import pytest


# Passing dataframe
@pytest.fixture
def df1_passing():
    return pd.DataFrame(
        {
            "BOROUGH": ["X", "Y"],
            "NEIGHBORHOOD": ["A", "B"],
            "BUILDING CLASS CATEGORY": ["C1", "C2"],
            "ADDRESS": ["addr1", "addr2"],
            "LAND SQUARE FEET": [100, 200],
            "GROSS SQUARE FEET": [200, 300],
            "SALE PRICE": [1000000, 2000000],
        }
    )


# DataFrame with an extra column
@pytest.fixture
def df2_extra_column():
    return pd.DataFrame(
        {
            "BOROUGH": ["Z"],
            "NEIGHBORHOOD": ["C"],
            "BUILDING CLASS CATEGORY": ["C3"],
            "ADDRESS": ["addr3"],
            "LAND SQUARE FEET": [300],
            "GROSS SQUARE FEET": [400],
            "SALE PRICE": [3000000],
            "EXTRA COLUMN": ["EXTRA"],
        }
    )


# DataFrame with a missing column
@pytest.fixture
def df_missing_column():
    return pd.DataFrame(
        {
            "BOROUGH": ["W"],
            "NEIGHBORHOOD": ["D"],
            "ADDRESS": ["addr4"],
            "LAND SQUARE FEET": [400],
            "GROSS SQUARE FEET": [500],
        }
    )


# One of the DataFrames has an extra column
def test_combineHousingDataSets_success(df1_passing, df2_extra_column):
    result = helpers.combineHousingDataSets([df1_passing, df2_extra_column])
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (
        3,
        8,
    )  # the combined DataFrame should have 3 rows and 8 columns
    # because we added a extra column from the original 7


# One of the DataFrames passed containes missing columns
def test_combineHousingDataSets_missing_columns(df1_passing, df_missing_column):
    assert helpers.combineHousingDataSets([df1_passing, df_missing_column]) == False


# --------------------------------------------------------
# TEST: filterOutliers()
# --------------------------------------------------------
import pandas as pd
import numpy as np
import pytest
import helpers


# Define a fixture for a simple sample DataFrame object
@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "SALE PRICE": [100, 200, 300, 400, np.nan],
            "GROSS SQUARE FEET": [100, 200, 300, 400, 500],
            "LAND SQUARE FEET": [
                "100",
                "200",
                "300",
                "400",
                "500",
            ],  # String data to test non-numeric column
        }
    )


@pytest.fixture
def sample_df_outliers():
    return pd.DataFrame(
        {
            "SALE PRICE": [
                100,
                200,
                300,
                400,
                500,
                600,
                700,
                800,
                900,
                1000,  # No outlier here
            ],
            "GROSS SQUARE FEET": [
                100,
                200,
                300,
                400,
                500,
                600,
                700,
                800,
                900,
                10000,  # Outlier
            ],
        }
    )


# Test that a ValueError is raised if a column in the
# thresholds parameter does not exist in the DataFrame
def test_missing_column(sample_df):
    with pytest.raises(
        ValueError, match="Column 'MISSING COLUMN' not found in DataFrame."
    ):
        helpers.filterOutliers(
            sample_df,
            {
                "MISSING COLUMN": 100
            },  # 'MISSING COLUMN does not exist in sample DataFrame'
            0.25,
            0.75,
        )


# Test that a ValueError is raised if a column in
# thresholds does not contain numeric data
def test_non_numeric_column(sample_df):
    with pytest.raises(ValueError, match="must contain numeric data."):
        helpers.filterOutliers(
            sample_df,
            {"LAND SQUARE FEET": 100},  # Column 'LAND SQUARE FEET' is non-numeric data
            0.25,
            0.75,
        )


# Test that the function works as expected with valid input
def test_valid_input(sample_df):
    thresholds = {"SALE PRICE": 150, "GROSS SQUARE FEET": 150}
    df_clean = helpers.filterOutliers(sample_df, thresholds, 0.25, 0.75)

    # Check that the cleaned DataFrame has the correct shape
    # (original df has 5 rows, 2 should be removed)
    # because of 'nan' value and thresholds
    assert df_clean.shape == (3, 3)

    # Check that the correct rows have been removed
    # (rows with SALE PRICE < 150 or GROSS SQUARE FEET < 150)
    assert df_clean["SALE PRICE"].min() == 200
    assert df_clean["GROSS SQUARE FEET"].min() == 200


# Testing the outlier removal
def test_outlier_removal(sample_df_outliers):
    thresholds = {"SALE PRICE": 100, "GROSS SQUARE FEET": 100}
    df_clean = helpers.filterOutliers(sample_df_outliers, thresholds, 0.25, 0.75)

    # Check that the cleaned DataFrame has the correct shape
    # (original df has 10 rows, 1 should be removed)
    assert df_clean.shape == (9, 2)

    # Check that the correct row has been removed
    # (row with 'GROSS SQUARE FEET' == 10000)
    assert 10000 not in df_clean["GROSS SQUARE FEET"].values


# --------------------------------------------------------
# TEST: Find missing geocodes
# --------------------------------------------------------

import config  # for SQL credentials
import time
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
from sqlalchemy import create_engine
from unittest.mock import patch


# Dataframe with three rows
@pytest.fixture
def dummy_local_geocodes_dataframe():
    return pd.DataFrame(
        {
            "BOROUGH CODE": [1, 1, 1],
            "BOROUGH": ["MANHATTAN", "MANHATTAN", "MANHATTAN"],
            "NEIGHBORHOOD": ["CHELSEA", "EAST VILLAGE", "HARLEM-CENTRAL"],
            "ADDRESS": [
                "254 WEST 27TH STREET",
                "46 STUYVESANT STREET, 1",
                "20 WEST 123 STREET",
            ],
            "PRIMARY_KEY": [
                "MANHATTAN_254 WEST 27TH STREET",
                "MANHATTAN_46 STUYVESANT STREET, 1",
                "MANHATTAN_20 WEST 123 STREET",
            ],
        }
    )


# Dummy gocode table SQL response with one row missing
# rel. to 'dummy_local_geocodes_dataframe'
@pytest.fixture
def dummy_sql_geocodes_table_response():
    return pd.DataFrame(
        {
            "BOROUGH CODE": [1, 1],
            "BOROUGH": ["MANHATTAN", "MANHATTAN"],
            "NEIGHBORHOOD": ["CHELSEA", "EAST VILLAGE"],
            "ADDRESS": ["254 WEST 27TH STREET", "46 STUYVESANT STREET, 1"],
            "LATITUDE": [1234, 1234],
            "LONGITUDE": [1234, 1234],
            "GEOCODING ERR": [False, False],
            "PRIMARY_KEY": [
                "MANHATTAN_254 WEST 27TH STREET",
                "MANHATTAN_46 STUYVESANT STREET, 1",
            ],
        }
    )


# Test for missing geo-columns in local DataFrame
def test_check_missing_rows_missing_columns_local_df(
    dummy_local_geocodes_dataframe, dummy_sql_geocodes_table_response
):
    # Declare desired result
    desired_row_data = {
        "BOROUGH CODE": [1],
        "BOROUGH": ["MANHATTAN"],
        "NEIGHBORHOOD": ["HARLEM-CENTRAL"],
        "ADDRESS": ["20 WEST 123 STREET"],
        "PRIMARY_KEY": ["MANHATTAN_20 WEST 123 STREET"],
        "LATITUDE": [None],
        "LONGITUDE": [None],
        "GEOCODING ERR": [False],
    }
    desired_df = pd.DataFrame(desired_row_data)

    # Test match
    with patch("pandas.read_sql_query") as mock_read:
        mock_read.return_value = dummy_sql_geocodes_table_response
        result = helpers.check_missing_rows(
            dummy_local_geocodes_dataframe, dummy_sql_geocodes_table_response, None
        )
        # Ensuring the result is a pandas.dataframe object
        assert isinstance(result, pd.DataFrame)

        # Ensuring we're getting the results we want...
        assert result.equals(desired_df)


"""
def test_check_missing_rows(dummy_sql_geocodes_table_response):
    local_df = # Add your local data here
    sql_table_name = # Add your SQL table name here
    engine = # Add your engine details here
    assert helpers.check_missing_rows(local_df, sql_table_name, engine) != False

    # We need to mock the data for the local_df and sql_table_name, and create a connection to the SQL database (engine).
    # Here we're just going to mock a few of them to illustrate the concept.
    local_df = pd.DataFrame({'BOROUGH CODE': [], 'BOROUGH': [], 'NEIGHBORHOOD': [], 'ADDRESS': []})
    sql_table_name = 'mock_table_name'
    engine = create_engine('sqlite:///:memory:') # Just a mock, replace with your real database connection

def test_check_missing_rows_sql_empty():
    # Mock an empty SQL database
    # FIXME: Detect "ValueError: SQL Database is empty"
    engine.execute(f"CREATE TABLE {sql_table_name} (PRIMARY_KEY text)")
    assert check_missing_rows(local_df, sql_table_name, engine) == False

def test_check_missing_rows_local_empty():
    # Mock an empty local DataFrame
    empty_df = pd.DataFrame()
    assert check_missing_rows(empty_df, sql_table_name, engine) == False

def test_check_missing_rows_primary_key_missing():
    # Mock a DataFrame without 'PRIMARY_KEY' column
    local_df_without_key = local_df.copy()
    local_df_without_key['PRIMARY_KEY'] = None
    assert check_missing_rows(local_df_without_key, sql_table_name, engine) == False

def test_check_missing_rows_no_missing_rows():
    # Mock a DataFrame and SQL table such that there are no missing rows
    local_df_with_key = local_df.copy()
    local_df_with_key['PRIMARY_KEY'] = local_df['BOROUGH'] + '_' + local_df['ADDRESS']
    engine.execute(f"INSERT INTO {sql_table_name} VALUES ('some_value')")
    assert check_missing_rows(local_df_with_key, sql_table_name, engine) == False
"""

# --------------------------------------------------------
# TEST: xx
# --------------------------------------------------------
