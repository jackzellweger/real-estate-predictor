# This script runs best on Debian

# Connect to EC2 instance
# For running from shell
#chmod 400 key-pair-1.pem
#ssh -i key-pair-1.pem admin@ec2-18-208-146-140.compute-1.amazonaws.com

# Nav to /opt folder
cd ../..//opt

# Changed permission of the opt folder 
sudo chown admin /opt

# Update everything
sudo apt upgrade -y

# Install git on the instance
sudo apt-get update -y
sudo apt-get install git -y
# git --version # Test if git is installed

# Install docker dependencies
sudo apt-get install gnupg2
sudo apt install apt-transport-https ca-certificates curl software-properties-common

# Adding gpg keys to docker
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o docker.gpg
sudo mv docker.gpg /etc/apt/trusted.gpg.d/

# Adding docker’s stable repo
echo "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list

# Update everything
sudo apt-get update

# Install Docker itself
sudo apt-get install docker-ce

# Verify that Docker is running (this doesn’t need to go into the script)
# sudo systemctl status docker

# Use pip to install docker compose
sudo apt-get install python3-pip -y
sudo pip install --upgrade docker-compose -y

# Get into the Ec2 SQL instance
#sudo docker exec -it real-estate-predictor_db_1 mysql -u user -p

#Password from compose.yaml 
#MYSQL_PASSWORD: password

# Clone the repo
sudo git clone https://github.com/jackzellweger/real-estate-predictor.git

# Navigate into project directory
cd real-estate-predictor

sudo docker-compose up --build

