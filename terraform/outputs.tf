# Output values for IoT Anomaly Detection System

# Project Information
output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# Pub/Sub Resources
output "pubsub_topic_name" {
  description = "Pub/Sub topic name for IoT data"
  value       = google_pubsub_topic.iot_data_topic.name
}

output "pubsub_subscription_name" {
  description = "Pub/Sub subscription name"
  value       = google_pubsub_subscription.iot_data_subscription.name
}

output "dead_letter_topic_name" {
  description = "Dead letter topic name"
  value       = google_pubsub_topic.dead_letter_topic.name
}

# BigQuery Resources
output "bigquery_dataset_id" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.iot_dataset.dataset_id
}

output "bigquery_sensor_table_id" {
  description = "BigQuery sensor readings table ID"
  value       = google_bigquery_table.sensor_readings_table.table_id
}

output "bigquery_ml_table_id" {
  description = "BigQuery ML predictions table ID"
  value       = google_bigquery_table.ml_predictions_table.table_id
}

output "bigquery_dataset_location" {
  description = "BigQuery dataset location"
  value       = google_bigquery_dataset.iot_dataset.location
}

# Storage Resources
output "ml_models_bucket_name" {
  description = "Cloud Storage bucket for ML models"
  value       = google_storage_bucket.ml_models_bucket.name
}

output "ml_models_bucket_url" {
  description = "Cloud Storage bucket URL for ML models"
  value       = google_storage_bucket.ml_models_bucket.url
}

output "data_backup_bucket_name" {
  description = "Cloud Storage bucket for data backups"
  value       = google_storage_bucket.data_backup_bucket.name
}

# Service Accounts
output "iot_main_service_account_email" {
  description = "Main IoT service account email"
  value       = google_service_account.iot_main_sa.email
}

output "iot_simulator_service_account_email" {
  description = "IoT simulator service account email"
  value       = google_service_account.iot_simulator_sa.email
}

output "data_consumer_service_account_email" {
  description = "Data consumer service account email"
  value       = google_service_account.data_consumer_sa.email
}

output "ml_trainer_service_account_email" {
  description = "ML trainer service account email"
  value       = google_service_account.ml_trainer_sa.email
}

output "ml_server_service_account_email" {
  description = "ML server service account email"
  value       = google_service_account.ml_server_sa.email
}

# Network Resources (if enabled)
output "vpc_network_name" {
  description = "VPC network name"
  value       = var.enable_compute_instances ? google_compute_network.iot_vpc[0].name : null
}

output "subnet_name" {
  description = "Subnet name"
  value       = var.enable_compute_instances ? google_compute_subnetwork.iot_subnet[0].name : null
}

output "subnet_cidr" {
  description = "Subnet CIDR range"
  value       = var.enable_compute_instances ? google_compute_subnetwork.iot_subnet[0].ip_cidr_range : null
}

# Monitoring Resources (if enabled)
output "monitoring_dashboard_url" {
  description = "URL to the monitoring dashboard"
  value       = var.enable_monitoring ? "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.iot_system_dashboard[0].id}?project=${var.project_id}" : null
}

output "notification_channel_name" {
  description = "Monitoring notification channel name"
  value       = var.enable_monitoring ? google_monitoring_notification_channel.email_channel[0].name : null
}

# Configuration for Docker Compose
output "docker_compose_env_vars" {
  description = "Environment variables for docker-compose.yml"
  value = {
    PROJECT_ID                = var.project_id
    TOPIC_NAME               = google_pubsub_topic.iot_data_topic.name
    SUBSCRIPTION_NAME        = google_pubsub_subscription.iot_data_subscription.name
    DATASET_ID              = google_bigquery_dataset.iot_dataset.dataset_id
    SENSOR_TABLE_ID         = google_bigquery_table.sensor_readings_table.table_id
    ML_PREDICTIONS_TABLE_ID = google_bigquery_table.ml_predictions_table.table_id
    ML_MODELS_BUCKET        = google_storage_bucket.ml_models_bucket.name
    GOOGLE_APPLICATION_CREDENTIALS = "/app/credentials.json"
  }
}

# URLs for accessing services (when running locally)
output "service_urls" {
  description = "URLs for accessing deployed services"
  value = {
    streamlit_dashboard = "http://localhost:8501"
    ml_server_api      = "http://localhost:8000"
    grafana_dashboard  = "http://localhost:3000"
    prometheus_metrics = "http://localhost:9090"
    jupyter_notebooks  = "http://localhost:8888"
  }
}

# BigQuery connection strings
output "bigquery_connection_info" {
  description = "BigQuery connection information"
  value = {
    dataset_full_id = "${var.project_id}.${google_bigquery_dataset.iot_dataset.dataset_id}"
    sensor_table_full_id = "${var.project_id}.${google_bigquery_dataset.iot_dataset.dataset_id}.${google_bigquery_table.sensor_readings_table.table_id}"
    ml_table_full_id = "${var.project_id}.${google_bigquery_dataset.iot_dataset.dataset_id}.${google_bigquery_table.ml_predictions_table.table_id}"
  }
}

# Pub/Sub connection strings
output "pubsub_connection_info" {
  description = "Pub/Sub connection information"
  value = {
    topic_full_name = "projects/${var.project_id}/topics/${google_pubsub_topic.iot_data_topic.name}"
    subscription_full_name = "projects/${var.project_id}/subscriptions/${google_pubsub_subscription.iot_data_subscription.name}"
  }
}

# Service account key (for development only - sensitive)
output "service_account_key_file" {
  description = "Path to service account key file"
  value       = local_file.iot_main_sa_key_file.filename
  sensitive   = true
}

# Cost estimation
output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown (USD)"
  value = {
    bigquery_storage = "~$20-50 (depends on data volume)"
    bigquery_queries = "~$5-15 (depends on query frequency)"
    pubsub_messages  = "~$5-10 (depends on message volume)"
    cloud_storage    = "~$1-5 (depends on model storage)"
    monitoring       = "~$0-5 (basic monitoring)"
    total_estimated  = "~$31-85 per month"
    note            = "Costs depend on actual usage patterns"
  }
}

# Quick start commands
output "quick_start_commands" {
  description = "Commands to get started with the system"
  value = {
    setup_credentials = "gcloud iam service-accounts keys create simulator/credentials.json --iam-account=${google_service_account.iot_main_sa.email}"
    start_system     = "docker-compose up -d"
    train_models     = "docker-compose run --rm ml-trainer python trainer.py"
    view_dashboard   = "open http://localhost:8501"
    check_status     = "docker-compose ps"
    view_logs        = "docker-compose logs -f"
  }
}