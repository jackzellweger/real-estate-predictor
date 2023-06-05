# Download main_local.sh file
# curl -o main_local.sh https://raw.githubusercontent.com/jackzellweger/real-estate-predictor/main/main_local.sh

# Change permissions of main_local.sh
sudo chmod +x ./main_local.sh

# Download the Terraform file
curl -o main.tf https://raw.githubusercontent.com/jackzellweger/real-estate-predictor/main/terraform/main.tf

# Move terraform file to terraform folder
sudo mkdir ./terraform
sudo mv main.tf ./terraform

# Move shell to terraform folder
cd ./terraform

# Prompt the user for inputs
read -p "Please enter your AWS access key: " AWS_ACCESS_KEY_ID_INPUT
read -p "Please enter your AWS secret access key: " AWS_SECRET_ACCESS_KEY_INPUT
# export AWS_ACCESS_KEY_ID=(your access key) && export AWS_SECRET_ACCESS_KEY=(your secret access key)

# Install Homebrew...
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Terraform
brew tap hashicorp/tap && brew install hashicorp/tap/terraform

# Initialize Terraform...
terraform init

# Plan the Terraform...
terraform plan

# Apply the Terraform...
terraform apply # FIXME: We might have trouble with this because we don't know the name of the AWS instance
