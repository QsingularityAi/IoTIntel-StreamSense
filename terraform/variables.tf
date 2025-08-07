variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# Pub/Sub Configuration
variable "pubsub_topic_name" {
  description = "Pub/Sub topic name for IoT data"
  type        = string
  default     = "iot-temp-vibration-data"
}

variable "pubsub_subscription_name" {
  description = "Pub/Sub subscription name for IoT data consumer"
  type        = string
  default     = "iot-temp-vibration-subscription"
}

variable "pubsub_dead_letter_topic" {
  description = "Pub/Sub dead letter topic name"
  type        = string
  default     = "iot-dead-letter-topic"
}

# BigQuery Configuration
variable "bigquery_dataset_id" {
  description = "BigQuery dataset ID for IoT data"
  type        = string
  default     = "iot_data"
}

variable "bigquery_table_id" {
  description = "BigQuery table ID for sensor readings"
  type        = string
  default     = "sensor_readings"
}

variable "bigquery_ml_table_id" {
  description = "BigQuery table ID for ML predictions"
  type        = string
  default     = "ml_predictions"
}

variable "bigquery_location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "US"
}

# Cloud Storage Configuration
variable "ml_model_bucket_name" {
  description = "GCS bucket name for ML models"
  type        = string
  default     = "iot-ml-models"
}

variable "data_backup_bucket_name" {
  description = "GCS bucket name for data backups"
  type        = string
  default     = "iot-data-backups"
}

# Service Account Configuration
variable "service_account_name" {
  description = "Service account name for IoT services"
  type        = string
  default     = "iot-anomaly-dataflow"
}

# Monitoring Configuration
variable "enable_monitoring" {
  description = "Enable Cloud Monitoring and Logging"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Log retention period in days"
  type        = number
  default     = 30
}

# ML Configuration
variable "ml_model_version" {
  description = "ML model version for deployment"
  type        = string
  default     = "v1.0.0"
}

variable "anomaly_threshold" {
  description = "Anomaly detection threshold"
  type        = number
  default     = 0.1
}

# Network Configuration
variable "vpc_name" {
  description = "VPC network name"
  type        = string
  default     = "iot-vpc"
}

variable "subnet_name" {
  description = "Subnet name"
  type        = string
  default     = "iot-subnet"
}

variable "subnet_cidr" {
  description = "Subnet CIDR range"
  type        = string
  default     = "10.0.0.0/24"
}

# Compute Configuration
variable "enable_compute_instances" {
  description = "Enable Compute Engine instances for processing"
  type        = bool
  default     = false
}

variable "compute_machine_type" {
  description = "Machine type for compute instances"
  type        = string
  default     = "e2-medium"
}

# Kubernetes Configuration (for future GKE deployment)
variable "enable_gke" {
  description = "Enable Google Kubernetes Engine cluster"
  type        = bool
  default     = false
}

variable "gke_cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "iot-ml-cluster"
}

variable "gke_node_count" {
  description = "Number of nodes in GKE cluster"
  type        = number
  default     = 3
}

# Security Configuration
variable "enable_private_google_access" {
  description = "Enable private Google access for subnets"
  type        = bool
  default     = true
}

variable "allowed_ip_ranges" {
  description = "IP ranges allowed to access resources"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Restrict this in production
}

# Cost Management
variable "budget_amount" {
  description = "Monthly budget amount in USD"
  type        = number
  default     = 100
}

variable "budget_alert_threshold" {
  description = "Budget alert threshold percentage"
  type        = number
  default     = 80
}
