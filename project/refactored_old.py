# Attempt to create database connection every 10 seconds for 100 seconds

max_retries = 10
retry_interval = 10  # in seconds

engine = None
retry_count = 0

while retry_count <= max_retries:
    try:
        engine = create_engine(f'mysql+pymysql://{username}:{password}@{hostname}')
        break  # Connection successful, exit the loop
    except Exception as e:
        if "Connection refused" in str(e):
            retry_count += 1
            print(f"Connection attempt {retry_count} failed. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
        else:
            raise

if engine is None:
    print("Max retries reached. Unable to establish a database connection.")
else:
    print("Database connection established successfully.")
    
# Create database and tables ------------------
try:
    with engine.connect() as connection:
        connection.execute(text(f'CREATE DATABASE {database_name};'))
except ProgrammingError:
    pass

# Reset connection to connect to specific database
engine = create_engine(f'mysql+pymysql://{username}:{password}@{hostname}/{database_name}')

# CREATE DATABASES ------------------

# Silence errors
os.environ['SQLALCHEMY_WARN_20'] = '0'
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'

# -------------- CREATE `geocodes` TABLE ---------------
geocodes_sql_table_name = 'geocodes'
with engine.connect() as connection:
    
    try:
        # Uses the geocode table backup if the table doesn't yet exist...
        geocodes_reset_df = pd.read_csv('geocodes_export_backup.csv')
        geocodes_reset_df.to_sql(geocodes_sql_table_name,
                                 con=engine,
                                 index=False,
                                 if_exists='fail')
    except:
        print(f"{geocodes_sql_table_name} table already exists. Not resetting!")
    
    try: # This will only work if there is not already a column called 'PRIMARY_KEY'
        connection.execute( # Set primary key
            text(
                f'ALTER TABLE {geocodes_sql_table_name} ADD COLUMN PRIMARY_KEY VARCHAR(255)'
            )
        )
        print(f"Column PRIMARY_KEY created in table {geocodes_sql_table_name}, database '{database_name}'.")
    except:
        print(f"Column PRIMARY_KEY already exists in in table {geocodes_sql_table_name}, database '{database_name}'.")
    
    try:
        connection.execute( # Set the values of the primary keys
            text(
                f'UPDATE {geocodes_sql_table_name} SET PRIMARY_KEY = CONCAT(`BOROUGH`, \'_\', `ADDRESS`)'
            )
        )
        print(f"PRIMARY_KEY column values set in database '{database_name}'.")
    except:
        print(f"PRIMARY_KEY column values set error in database '{database_name}'.") 
        
# 2.) -------------- CREATE `cat_map` TABLE ---------------
mapping_list = [(k, v) for k, vals in helpers.mapping.items() for v in vals]
mapping_df = pd.DataFrame(
    mapping_list,
    columns=['ZILLOW CATEGORY', 'BUILDING CLASS CATEGORY']
)
with engine.connect() as connection:
    # Put the map into a SQL table. Why? Not sure. Might need it later!
    mapping_df.to_sql('cat_map', con=engine, index=False, if_exists='replace')
