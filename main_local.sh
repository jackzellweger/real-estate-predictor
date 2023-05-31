curl -o main.tf https://raw.githubusercontent.com/jackzellweger/real-estate-predictor/main/terraform/main.tf


# Change permissions of the file they just downloaded
sudo chmod +x ./main_local.sh

# Prompt the user for inputs
read -p "Please enter your AWS access key: " AWS_ACCESS_KEY_ID_INPUT
read -p "Please enter your AWS secret access key: " AWS_SECRET_ACCESS_KEY_INPUT
# export AWS_ACCESS_KEY_ID=(your access key) && export AWS_SECRET_ACCESS_KEY=(your secret access key)

# Install Homebrew...
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Terraform
brew tap hashicorp/tap && brew install hashicorp/tap/terraform

# Download Terraform file they will need...
curl -o main.tf https://raw.githubusercontent.com/jackzellweger/real-estate-predictor/main/terraform/main.tf

#terraform main.tf...