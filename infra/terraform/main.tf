terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

locals {
  prefix = "geo-${random_string.suffix.result}"
}

resource "azurerm_resource_group" "main" {
  name     = "${local.prefix}-rg"
  location = var.location
}

resource "azurerm_postgresql_flexible_server" "postgis" {
  name                         = "${local.prefix}-postgis"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "16"
  administrator_login          = var.db_admin
  administrator_password       = var.db_password
  sku_name                     = "B_Standard_B1ms"
  storage_mb                   = 32768
  geo_redundant_backup_enabled = false

  depends_on = [azurerm_resource_group.main]
}

resource "azurerm_postgresql_flexible_server_database" "geospatial" {
  name      = "geospatial"
  server_id = azurerm_postgresql_flexible_server.postgis.id
  charset   = "UTF8"

  depends_on = [azurerm_postgresql_flexible_server.postgis]
}

resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure" {
  name             = "AllowAzureServices"
  server_id        = azurerm_postgresql_flexible_server.postgis.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

resource "azurerm_storage_account" "datalake" {
  name                     = replace("${local.prefix}dl", "-", "")
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "gps_archive" {
  name                  = "gps-archive"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "h3_aggregations" {
  name                  = "h3-aggregations"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

resource "azurerm_container_group" "kafka" {
  name                = "${local.prefix}-kafka"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  ip_address_type     = "Public"
  dns_name_label      = local.prefix

  container {
    name   = "kafka"
    image  = "apache/kafka:3.9.0"
    cpu    = 1.0
    memory = 2.0

    environment_variables = {
      CLUSTER_ID                        = "geo-az-cluster"
      KAFKA_NODE_ID                     = "1"
      KAFKA_PROCESS_ROLES               = "broker,controller"
      KAFKA_LISTENERS                   = "PLAINTEXT://:9092,CONTROLLER://:9093"
      KAFKA_ADVERTISED_LISTENERS        = "PLAINTEXT://kafka:9092"
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR = "1"
      KAFKA_NUM_PARTITIONS              = "6"
    }

    ports {
      port     = 9092
      protocol = "TCP"
    }
  }
}

resource "azurerm_container_group" "api" {
  name                = "${local.prefix}-api"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  ip_address_type     = "Public"
  dns_name_label      = "${local.prefix}-api"

  container {
    name   = "api"
    image  = "python:3.12-slim"
    cpu    = 0.5
    memory = 1.0

    commands = [
      "bash", "-c",
      "pip install -q fastapi uvicorn && uvicorn geofence_api:app --host 0.0.0.0 --port 8000",
    ]

    ports {
      port     = 8000
      protocol = "TCP"
    }
  }
}

output "kafka_endpoint" {
  value = "${azurerm_container_group.kafka.fqdn}:9092"
}

output "api_endpoint" {
  value = "http://${azurerm_container_group.api.fqdn}:8000"
}

output "postgis_server" {
  value = azurerm_postgresql_flexible_server.postgis.fqdn
}

output "storage_account" {
  value = azurerm_storage_account.datalake.name
}
