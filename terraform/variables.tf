variable "aws_region" {
  description = "AWS region where the infrastructure will be created"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name used for resource names and tags"
  type        = string
  default     = "number-guess-api"
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "production"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "Raz0er"
}

variable "github_repository" {
  description = "GitHub repository name"
  type        = string
  default     = "number-guess-api"
}

variable "github_branch" {
  description = "GitHub branch allowed to assume the AWS deployment role"
  type        = string
  default     = "main"
}