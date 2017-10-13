terraform {
  required_version = ">= 0.10.0"
}

provider "aws" {
  region = "${var.aws_region}"
}
