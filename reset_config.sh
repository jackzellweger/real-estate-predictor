# Prompt the user for inputs
read -p "Please enter your Google API Key: " GOOGLE_API_KEY
read -p "Please enter your database username: " DB_USERNAME
read -sp "Please enter your database password: " DB_PASSWORD  # -s flag hides input for privacy
echo  # Insert a line break
read -p "Please enter your database name: " DB_NAME

# Write the variables to a new Python file
cat << EOF > ./project/config.py
GOOGLE_API_KEY = "$GOOGLE_API_KEY"
DB_USERNAME = "$DB_USERNAME"
DB_PASSWORD = "$DB_PASSWORD"
DB_HOSTNAME = "db"
DB_NAME = "$DB_NAME"
EOF