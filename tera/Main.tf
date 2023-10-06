# store the terraform state file in s3
terraform {
  backend "s3" {
    bucket  = "dj-start-remote-state"
    key     = "gh_actions/terraform.tfstate"
    region  = "us-east-1"
    profile = "default"
  }
}

provider "random" {}


provider "aws" {
  region  = "us-east-1"
  profile = "default"
}