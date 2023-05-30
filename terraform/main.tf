# ---- Variables
variable "server_port" {
  description = "The port the server will use for HTTP requests"
  type        = number
  default     = 8080
}

# ---- Provider
provider "aws" {
  region = "us-east-2"
}

# ---- Resources

# AWS Instance
resource "aws_instance" "api" {
  ami           =  "ami-08eda224ab7296253" 

  instance_type = "t2.xlarge"

  key_name      = "key-pair-7"

  vpc_security_group_ids = [aws_security_group.instance.id]
  
  user_data = <<-EOF
                #!/bin/bash
                cd ../..//opt && \
                sudo chown admin /opt && \
                sudo apt upgrade -y && \
                sudo apt-get update -y && \
                sudo apt-get install git -y && \
                sudo git clone https://github.com/jackzellweger/real-estate-predictor.git && \
                cd real-estate-predictor && \
                sudo chmod +x ./main.sh && \
                sudo ./main.sh
              EOF
  
  user_data_replace_on_change = true

  tags = {
    Name = "real-estate-predictor"
  }
}

# Security group 
resource "aws_security_group" "instance" {
  name = "real-estate-predictor"
  
  # API ingress
  ingress {
    from_port   = var.server_port
    to_port     = var.server_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # SSH ingress for development
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Egress allows all traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

