#!/bin/sh
# This script runs best on Debian

# Install docker dependencies
sudo apt-get install \
  -y \
  gnupg2

sudo apt install \
  -y \
  apt-transport-https \
  ca-certificates \
  curl \
  software-properties-common \

# Adding gpg keys to docker
sudo curl \
  -fsSL \
  https://download.docker.com/ \
  linux/debian/gpg -o docker.gpg && \
  sudo mv docker.gpg /etc/apt/trusted.gpg.d/

# Adding docker’s stable repo
echo "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list

# Update everything
sudo apt-get update

# Set up Docker repo
sudo apt-get update && sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
sudo docker run hello-world

# Use pip to install docker compose
sudo apt-get install python3-pip -y
sudo pip install --upgrade docker-compose

# Prompt the user for inputs
read -p "Please enter your Google API Key: " GOOGLE_API_KEY
read -p "Please enter your database username: " DB_USERNAME
read -p "Please enter your database password: " DB_PASSWORD 
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

# Build the compose file
sudo docker-compose up --build -d

# Wait until docker containers are ready....
echo "Waiting until Docker containers are ready... (30s)"
sleep 30s

# RUN DATA PROCESSING PYTHON SCRIPT

# Specify path to notebook
NOTEBOOK_PATH=./notebook.ipynb # We're in the `./project` folder in the container at this point
CONTAINER_NAME=real-estate-predictor_processor_1

# Run the command on the container
echo "Running data processor script..."
sudo docker exec $CONTAINER_NAME sh -c "jupyter nbconvert --execute $NOTEBOOK_PATH --to python"
echo "Data processor script complete..."

# Copy model and encoder to flask server directory
sudo cp ./project/model.joblib ./project/model/model.joblib && sudo cp ./project/preprocessor.joblib ./project/model/preprocessor.joblib

# Print jupyter notebook access token
echo "Your Jupyter development env can be accessed with this following token..."
sudo docker exec -it real-estate-predictor_processor_1 jupyter-notebook list

# Define the cron job
# CRON_JOB="0 0 1 * * cd opt/real-estate-predictor/project && python3 notebook.py && cp -r model/ flask_app/model/"

# Add the cron job to the user's crontab, preserving existing jobs
# (crontab -l; echo "$CRON_JOB") | crontab -

# Write the cron job to the user's crontab, overwriting existing jobs
# echo "$CRON_JOB" | crontab -

echo "Restarting server with new configuration..."
sudo docker container restart real-estate-predictor_flask-server_1

echo "The prediction API is available at..."
echo -n "http://" ; curl -s ipinfo.io/ip ; echo ":8080/predict"
