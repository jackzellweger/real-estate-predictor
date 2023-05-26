#!/bin/sh

# This script runs best on Debian

# Connect to EC2 instance
# For running from shell
#chmod 400 key-pair-1.pem
#ssh -i key-pair-1.pem admin@ec2-18-208-146-140.compute-1.amazonaws.com

# Run this scrpt 
# cd ../..//opt && sudo chown admin /opt && sudo apt upgrade -y && sudo apt-get update -y && sudo apt-get install git -y && sudo git clone https://github.com/jackzellweger/real-estate-predictor.git && cd real-estate-predictor

sudo chmod +x main.sh

# Install docker dependencies
sudo apt-get install gnupg2 -y
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y

# Adding gpg keys to docker
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o docker.gpg && sudo mv docker.gpg /etc/apt/trusted.gpg.d/

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

# Verify that Docker is running (this doesn’t need to go into the script)
# sudo systemctl status docker

# Use pip to install docker compose
sudo apt-get install python3-pip -y
sudo pip install --upgrade docker-compose

# Get into the Ec2 SQL instance
#sudo docker exec -it real-estate-predictor_db_1 mysql -u user -p

#Password from compose.yaml 
#MYSQL_PASSWORD: password

# Build the compose file
sudo docker-compose up --build

