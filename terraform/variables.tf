variable "aws_region" {
  description = "Region AWS dla infrastruktury"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Nazwa projektu używana w nazwach zasobów"
  type        = string
  default     = "number-guess-api"
}

variable "environment" {
  description = "Nazwa środowiska"
  type        = string
  default     = "production"
}

variable "instance_type" {
  description = "Typ instancji EC2"
  type        = string
  default     = "t3.micro"
}

variable "allowed_ssh_cidr" {
  description = "Publiczny adres IP dopuszczony do SSH, zakończony /32"
  type        = string
}

variable "public_key_path" {
  description = "Ścieżka do publicznego klucza SSH"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}
