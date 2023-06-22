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
# TEST: Find missing geocodes in SQL table
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


# Geocode dataframe with three rows
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


# Test for proper response in the case of
# missing geo-columns in the SQL query relative
# to the local DataFrame
def test_check_missing_rows(
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


# Empty SQL response
def test_check_missing_rows_empty_sql_query(dummy_local_geocodes_dataframe):
    with patch("pandas.read_sql_query") as mock_read:
        mock_read.return_value = pd.DataFrame()
        with pytest.raises(ValueError, match="SQL Database is empty"):
            helpers.check_missing_rows(
                dummy_local_geocodes_dataframe, dummy_sql_geocodes_table_response, None
            )


# Missing columns in SQL response
def test_check_missing_rows_missing_columns_sql_response(
    dummy_local_geocodes_dataframe, dummy_sql_geocodes_table_response
):
    # Test response if incorrect SQL columns are not present
    with patch("pandas.read_sql_query") as mock_read:
        mock_read.return_value = dummy_sql_geocodes_table_response.drop(
            "LATITUDE", axis=1
        )
        with pytest.raises(KeyError, match="Columns are missing in SQL response"):
            helpers.check_missing_rows(dummy_local_geocodes_dataframe, None, None)


# Missing columns in local DataFrame
def test_check_missing_rows_missing_columns_local_df(
    dummy_local_geocodes_dataframe, dummy_sql_geocodes_table_response
):
    # Test response if incorrect local columns are not present
    with patch("pandas.read_sql_query") as mock_read:
        mock_read.return_value = dummy_sql_geocodes_table_response
        with pytest.raises(KeyError, match="Columns are missing in local Dataframe"):
            helpers.check_missing_rows(
                dummy_local_geocodes_dataframe.drop("BOROUGH", axis=1),
                None,
                None,
            )


# --------------------------------------------------------
# TEST: Geocode row of address data
# --------------------------------------------------------

# Imports
from pandas._testing import assert_series_equal
import importlib
import config

# Reload config for good measure
importlib.reload(config)


# Fixture to mock a row
# (this address does not exist)
@pytest.fixture
def row():
    return pd.Series(
        {
            "ADDRESS": "123 Main St",
            "BOROUGH": "Manhattan",
            "GEOCODING ERR": False,
            "LATITUDE": None,
            "LONGITUDE": None,
        }
    )


@pytest.fixture
def expected_row():
    return pd.Series(
        {
            "ADDRESS": "2744 BOUCK AVE",
            "BOROUGH": "BRONX",
            "GEOCODING ERR": False,
            "LATITUDE": 40.866652,
            "LONGITUDE": -73.849797,
        }
    )


# Test a sucessful geolocation
def test_geolocate_success(row):
    # Mock successful geocoding response
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "results": [
                {
                    "geometry": {"location": {"lat": 40.7128, "lng": -74.0060}},
                    "partial_match": False,  # Partial match is 'False' because we're mocking a full match
                }
            ]
        }

        result = helpers.geolocate(row, config.GOOGLE_API_KEY)

        expected = pd.Series(
            {
                "ADDRESS": "123 Main St",
                "BOROUGH": "Manhattan",
                "GEOCODING ERR": False,
                "LATITUDE": 40.7128,
                "LONGITUDE": -74.0060,
            }
        )
    # Asserts that result DataFrame equals expected DataFrame
    assert_series_equal(result, expected)


# Test geolocation result marking total API failure
# by setting 'GEOCODING ERR' as 'True'
def test_geolocate_failure_no_results(row):
    # Mock failure geocoding response with no results
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"results": []}

        result = helpers.geolocate(row, config.GOOGLE_API_KEY)

        expected = pd.Series(
            {
                "ADDRESS": "123 Main St",
                "BOROUGH": "Manhattan",
                "GEOCODING ERR": True,
                "LATITUDE": None,
                "LONGITUDE": None,
            }
        )
    # Asserts that result DataFrame equals expected DataFrame
    assert_series_equal(result, expected)


# Test if 'GEOCODING ERR' is marked as 'True'
# if there is only a partial match
def test_geolocate_failure_partial_match(row):
    # Mock failure geocoding response with partial match
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "results": [
                {
                    "geometry": {"location": {"lat": 40.7128, "lng": -74.0060}},
                    "partial_match": True,
                }
            ]
        }

        result = helpers.geolocate(row, config.GOOGLE_API_KEY)

        expected = pd.Series(
            {
                "ADDRESS": "123 Main St",
                "BOROUGH": "Manhattan",
                "GEOCODING ERR": True,
                "LATITUDE": None,
                "LONGITUDE": None,
            }
        )
    # Asserts that result DataFrame equals expected DataFrame
    assert_series_equal(result, expected)


def test_geolocate_return_expected_result(expected_row):
    # Creating a row we'll pass to the function
    row_to_pass = expected_row.copy()
    row_to_pass["LATITUDE"] = None
    row_to_pass["LONGITUDE"] = None

    # Pass the row
    result = helpers.geolocate(row_to_pass, config.GOOGLE_API_KEY)

    # Assert the result is what we expect
    assert_series_equal(result, expected_row)


# --------------------------------------------------------
# TEST: Is the local DataFrame a subset of the SQL table?
# --------------------------------------------------------
from unittest.mock import MagicMock, patch, create_autospec
from sqlalchemy.engine import Engine


@pytest.fixture
def sql_response_df():
    return pd.DataFrame(
        {
            "ADDRESS": ["123 Main St", "456 Main St", "789 Main St"],
            "BOROUGH": ["Manhattan", "Brooklyn", "Queens"],
            "GEOCODING ERR": [True, True, False],
            "LATITUDE": [None, None, 40.7282],
            "LONGITUDE": [None, None, -73.7949],
            "PRIMARY_KEY": [
                "Manhattan_123 Main St",
                "Brooklyn_456 Main St",
                "Queens_789 Main St",
            ],
        }
    )


# Test to ensure False return value if we removea row
# from the SQL table that is in the local DataFrame
# Also tests to ensure False return value if we add a new
# row to the local DataFrame so it’s no longer a subset
# of the SQL table.
def test_is_local_sql_subset_fail(sql_response_df):
    mock_engine = create_autospec(Engine)

    # When connect is called, it should return a context manager
    # that produces a MagicMock when used in a with block.
    mock_connection = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    # Test case 1: Local DataFrame is not a subset
    # because we remove a row in the SQL table that
    # is in the local DataFrame
    with patch("pandas.read_sql_query") as mock_read:
        mock_read.return_value = sql_response_df.drop(
            sql_response_df.index[1]
        )  # Drop the second row to set up a False result

        local_df = sql_response_df  # Setting local to response

        result = helpers.is_local_sql_subset(
            mock_engine, local_df, "geocodes_table_name"
        )

    # Assertion criteria
    assert result == False

    # Test case 2: Defining a new row to the local
    # DataFrame so that we are no longer in subset,
    # and we fail the test

    new_row = {
        "ADDRESS": "321 Park Ave",
        "BOROUGH": "Queens",
        "GEOCODING ERR": False,
        "LATITUDE": 40.7389,
        "LONGITUDE": -73.8816,
        "PRIMARY_KEY": "Queens_321 Park Ave",
    }
    new_row = pd.Series(new_row)

    with patch("pandas.read_sql_query") as mock_read:
        mock_read.return_value = sql_response_df

        # Adding the new row to the local DataFrame
        local_df_1 = pd.concat([sql_response_df, new_row], ignore_index=True)

        result_1 = helpers.is_local_sql_subset(
            mock_engine, local_df_1, "geocodes_table_name"
        )
    # This should return False because
    assert result_1 == False


def test_is_local_sql_subset_success(sql_response_df):
    mock_engine = create_autospec(Engine)

    # When connect is called, it should return a context manager
    # that produces a MagicMock when used in a with block.
    mock_connection = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_connection

    # Mocks a local DataFrame that is a subset of the SQL table return table
    local_df = sql_response_df.drop(sql_response_df.index[1])

    with patch("pandas.read_sql_query") as mock_read:
        mock_read.return_value = sql_response_df

        result = helpers.is_local_sql_subset(
            mock_engine,
            local_df,
            "geocodes_table_name",
        )  # Inserting None because we mocked the reads

    # Assertion criteria
    assert result == True
