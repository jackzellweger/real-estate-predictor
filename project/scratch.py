# Reset
# combined.to_csv('sales.csv', index=False)
combined = pd.read_csv('sales.csv')
combined.insert(combined.columns.get_loc(
    'BUILDING CLASS CATEGORY') + 1, 'ZILLOW CATEGORY', None)

# HELPERS
import importlib
importlib.reload(helpers)
invert_mapping

# Inverting the dictionary
invert_mapping = {building_class: zillow_cat for zillow_cat, building_class_list in helpers.intermediary_mapping.items() for building_class in building_class_list}

# Now, map the BUILDING CLASS CATEGORY column in combined dataframe
combined['ZILLOW CATEGORY'] = combined['BUILDING CLASS CATEGORY'].map(invert_mapping).copy()

# FEATURE ENGINEERING

# First, create the inverted mapping dictionary, as before
invert_mapping = {building_class: zillow_cat for zillow_cat, building_class_list in helpers.intermediary_mapping.items() for building_class in building_class_list}

# Then, use the map function to create the new column
combined['GROUPED CATEGORY'] = combined['BUILDING CLASS CATEGORY'].map(invert_mapping)

# Check if there are any missing values in the new column (i.e., categories that couldn't be mapped)
if combined['GROUPED CATEGORY'].isna().any():
    print("Warning: some categories could not be mapped!")

combined = combined.dropna(subset=['ZILLOW CATEGORY'])

combined