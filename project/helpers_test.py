# --------------------------------------------------------
# TEST: xx
# --------------------------------------------------------

# ... Code goes here ...

# --------------------------------------------------------
# TEST: combineHousingDataSets()
# --------------------------------------------------------

import helpers
import pandas as pd
import pytest

# Passing DataFrame
df1_passing = pd.DataFrame(
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
df2_extra_column = pd.DataFrame(
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
df_missing_column = pd.DataFrame(
    {
        "BOROUGH": ["W"],
        "NEIGHBORHOOD": ["D"],
        "ADDRESS": ["addr4"],
        "LAND SQUARE FEET": [400],
        "GROSS SQUARE FEET": [500],
    }
)


# One of the DataFrames has an extra column
def test_combineHousingDataSets_success():
    result = helpers.combineHousingDataSets([df1_passing, df2_extra_column])
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (
        3,
        8,
    )  # the combined DataFrame should have 3 rows and 8 columns
    # because we added a extra column from the original 7


# One of the DataFrames passed containes missing columns
def test_combineHousingDataSets_missing_columns():
    assert helpers.combineHousingDataSets([df1_passing, df_missing_column]) == False


# --------------------------------------------------------
# TEST: filterOutliers()
# --------------------------------------------------------
import pandas as pd
import numpy as np
import pytest
import helpers


# Define a fixture for a simple DataFrame for testing
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


# Test that a ValueError is raised if a column in thresholds does not exist in the DataFrame
def test_missing_column(sample_df):
    with pytest.raises(
        ValueError, match="Column 'MISSING COLUMN' not found in DataFrame."
    ):
        filterOutliers(sample_df, {"MISSING COLUMN": 100}, 0.25, 0.75)


# Test that a ValueError is raised if a column in thresholds does not contain numeric data
def test_non_numeric_column(sample_df):
    with pytest.raises(
        ValueError, match="Column 'LAND SQUARE FEET' must contain numeric data."
    ):
        filterOutliers(sample_df, {"LAND SQUARE FEET": 100}, 0.25, 0.75)


# Test that the function works as expected with valid input
def test_valid_input(sample_df):
    thresholds = {"SALE PRICE": 150, "GROSS SQUARE FEET": 150}
    df_clean = filterOutliers(sample_df, thresholds, 0.25, 0.75)

    # Check that the cleaned DataFrame has the correct shape (original df has 5 rows, 2 should be removed)
    assert df_clean.shape == (3, 3)

    # Check that the correct rows have been removed (rows with SALE PRICE < 150 or GROSS SQUARE FEET < 150)
    assert df_clean["SALE PRICE"].min() == 200
    assert df_clean["GROSS SQUARE FEET"].min() == 200
