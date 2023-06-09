import pandas as pd
import helpers


# Borough, Neighborhood, Building Class Category Address Land Square
# Feet, Gross Square Feet, Sale Price
def test_combineHousingDataSetsBadColumns():
    dataTables = [
        pd.DataFrame({"CITY": ["Manhattan", "Manhattan"]}),
    ]
    assert helpers.combineHousingDataSets(dataTables) == False
