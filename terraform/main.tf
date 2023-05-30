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
resource "aws_instance" "example" {
  ami           =  "ami-08eda224ab7296253" 

  instance_type = "t2.xlarge"

  key_name      = "key-pair-7"

  vpc_security_group_ids = [aws_security_group.instance.id]
  
  user_data = <<-EOF
              #!/bin/bash
              echo "Hello, World" > index.html
              nohup busybox httpd -f -p var.server_port &
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

