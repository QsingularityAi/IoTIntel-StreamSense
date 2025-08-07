terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "pubsub.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "iam.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "compute.googleapis.com"
  ])

  service = each.value
  project = var.project_id

  disable_dependent_services = true
  disable_on_destroy         = false
}

# VPC Network
resource "google_compute_network" "iot_vpc" {
  count                   = var.enable_compute_instances ? 1 : 0
  name                    = var.vpc_name
  auto_create_subnetworks = false
  project                 = var.project_id

  depends_on = [google_project_service.required_apis]
}

# Subnet
resource "google_compute_subnetwork" "iot_subnet" {
  count         = var.enable_compute_instances ? 1 : 0
  name          = var.subnet_name
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.iot_vpc[0].id
  project       = var.project_id

  private_ip_google_access = var.enable_private_google_access
}

# Firewall rules
resource "google_compute_firewall" "allow_internal" {
  count   = var.enable_compute_instances ? 1 : 0
  name    = "allow-internal-iot"
  network = google_compute_network.iot_vpc[0].name
  project = var.project_id

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = [var.subnet_cidr]
}

# Pub/Sub Topic for IoT data
resource "google_pubsub_topic" "iot_data_topic" {
  name    = var.pubsub_topic_name
  project = var.project_id

  labels = {
    environment = var.environment
    component   = "iot-data-pipeline"
  }

  depends_on = [google_project_service.required_apis]
}

# Dead letter topic
resource "google_pubsub_topic" "dead_letter_topic" {
  name    = var.pubsub_dead_letter_topic
  project = var.project_id

  labels = {
    environment = var.environment
    component   = "iot-data-pipeline"
  }

  depends_on = [google_project_service.required_apis]
}

# Pub/Sub Subscription for data consumer
resource "google_pubsub_subscription" "iot_data_subscription" {
  name    = var.pubsub_subscription_name
  topic   = google_pubsub_topic.iot_data_topic.name
  project = var.project_id

  # Acknowledge deadline in seconds
  ack_deadline_seconds = 20

  # Message retention duration in seconds
  message_retention_duration = "604800s" # 7 days

  # Dead letter policy
  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter_topic.id
    max_delivery_attempts = 5
  }

  # Retry policy
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  labels = {
    environment = var.environment
    component   = "iot-data-pipeline"
  }
}

# BigQuery Dataset for IoT data
resource "google_bigquery_dataset" "iot_dataset" {
  dataset_id  = var.bigquery_dataset_id
  project     = var.project_id
  location    = var.bigquery_location
  description = "IoT sensor data and ML predictions"

  labels = {
    environment = var.environment
    component   = "iot-data-warehouse"
  }

  # Access control
  access {
    role          = "OWNER"
    user_by_email = google_service_account.iot_main_sa.email
  }

  access {
    role          = "WRITER"
    user_by_email = google_service_account.data_consumer_sa.email
  }

  access {
    role          = "READER"
    user_by_email = google_service_account.ml_trainer_sa.email
  }

  depends_on = [google_project_service.required_apis]
}

# BigQuery Table for sensor readings
resource "google_bigquery_table" "sensor_readings_table" {
  dataset_id = google_bigquery_dataset.iot_dataset.dataset_id
  table_id   = var.bigquery_table_id
  project    = var.project_id

  description = "Real-time IoT sensor readings"

  labels = {
    environment = var.environment
    component   = "iot-data-warehouse"
  }

  # Time partitioning for better performance
  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  # Clustering for query optimization
  clustering = ["device_id", "building"]

  schema = jsonencode([
    {
      name        = "device_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Unique device identifier"
    },
    {
      name        = "timestamp"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Reading timestamp"
    },
    {
      name        = "building"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Building identifier"
    },
    {
      name        = "floor"
      type        = "INTEGER"
      mode        = "REQUIRED"
      description = "Floor number"
    },
    {
      name        = "room"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Room identifier"
    },
    {
      name        = "device_type"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Type of IoT device"
    },
    {
      name        = "temperature"
      type        = "FLOAT"
      mode        = "REQUIRED"
      description = "Temperature reading in Celsius"
    },
    {
      name        = "vibration"
      type        = "FLOAT"
      mode        = "REQUIRED"
      description = "Vibration reading in mm/s RMS"
    },
    {
      name        = "is_anomaly"
      type        = "BOOLEAN"
      mode        = "NULLABLE"
      description = "Whether reading is flagged as anomaly"
    },
    {
      name        = "anomaly_type"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Type of anomaly detected"
    }
  ])
}

# BigQuery Table for ML predictions
resource "google_bigquery_table" "ml_predictions_table" {
  dataset_id = google_bigquery_dataset.iot_dataset.dataset_id
  table_id   = var.bigquery_ml_table_id
  project    = var.project_id

  description = "ML model predictions and anomaly scores"

  labels = {
    environment = var.environment
    component   = "iot-ml-predictions"
  }

  # Time partitioning
  time_partitioning {
    type  = "DAY"
    field = "prediction_timestamp"
  }

  schema = jsonencode([
    {
      name        = "device_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Device identifier"
    },
    {
      name        = "prediction_timestamp"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "When prediction was made"
    },
    {
      name        = "model_version"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "ML model version used"
    },
    {
      name        = "temperature_anomaly_score"
      type        = "FLOAT"
      mode        = "NULLABLE"
      description = "Temperature anomaly score"
    },
    {
      name        = "vibration_anomaly_score"
      type        = "FLOAT"
      mode        = "NULLABLE"
      description = "Vibration anomaly score"
    },
    {
      name        = "is_temp_anomaly"
      type        = "BOOLEAN"
      mode        = "NULLABLE"
      description = "Temperature anomaly flag"
    },
    {
      name        = "is_vibration_anomaly"
      type        = "BOOLEAN"
      mode        = "NULLABLE"
      description = "Vibration anomaly flag"
    },
    {
      name        = "overall_anomaly"
      type        = "BOOLEAN"
      mode        = "NULLABLE"
      description = "Overall anomaly flag"
    }
  ])
}

# Main service account for IoT operations
resource "google_service_account" "iot_main_sa" {
  account_id   = var.service_account_name
  display_name = "IoT Anomaly Detection Main Service Account"
  description  = "Main service account for IoT anomaly detection system"
  project      = var.project_id
}

# Service account for IoT simulator
resource "google_service_account" "iot_simulator_sa" {
  account_id   = "iot-simulator-sa"
  display_name = "IoT Simulator Service Account"
  description  = "Service account for IoT data simulator"
  project      = var.project_id
}

# Service account for data consumer
resource "google_service_account" "data_consumer_sa" {
  account_id   = "data-consumer-sa"
  display_name = "Data Consumer Service Account"
  description  = "Service account for Pub/Sub data consumer"
  project      = var.project_id
}

# Service account for ML trainer
resource "google_service_account" "ml_trainer_sa" {
  account_id   = "ml-trainer-sa"
  display_name = "ML Trainer Service Account"
  description  = "Service account for ML model training"
  project      = var.project_id
}

# Service account for ML server
resource "google_service_account" "ml_server_sa" {
  account_id   = "ml-server-sa"
  display_name = "ML Server Service Account"
  description  = "Service account for ML prediction server"
  project      = var.project_id
}

# Cloud Storage bucket for ML models
resource "google_storage_bucket" "ml_models_bucket" {
  name     = "${var.project_id}-${var.ml_model_bucket_name}"
  location = var.region
  project  = var.project_id

  labels = {
    environment = var.environment
    component   = "ml-models"
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.required_apis]
}

# Cloud Storage bucket for data backups
resource "google_storage_bucket" "data_backup_bucket" {
  name     = "${var.project_id}-${var.data_backup_bucket_name}"
  location = var.region
  project  = var.project_id

  labels = {
    environment = var.environment
    component   = "data-backup"
  }

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.required_apis]
}
