variable "location" {
  description = "Azure region"
  type        = string
  default     = "westeurope"
}

variable "db_admin" {
  description = "PostgreSQL admin username"
  type        = string
  default     = "geo_admin"
}

variable "db_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
  default     = "GeoPass123!"
}
