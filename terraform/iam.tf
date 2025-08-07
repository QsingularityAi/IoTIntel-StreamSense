# IAM roles and permissions for IoT Anomaly Detection System

# Main service account IAM bindings
resource "google_project_iam_member" "iot_main_sa_roles" {
  for_each = toset([
    "roles/bigquery.admin",
    "roles/pubsub.admin",
    "roles/storage.admin",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.iot_main_sa.email}"
}

# IoT Simulator service account permissions
resource "google_project_iam_member" "iot_simulator_sa_roles" {
  for_each = toset([
    "roles/pubsub.publisher",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.iot_simulator_sa.email}"
}

# Data Consumer service account permissions
resource "google_project_iam_member" "data_consumer_sa_roles" {
  for_each = toset([
    "roles/pubsub.subscriber",
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.data_consumer_sa.email}"
}

# ML Trainer service account permissions
resource "google_project_iam_member" "ml_trainer_sa_roles" {
  for_each = toset([
    "roles/bigquery.dataViewer",
    "roles/bigquery.jobUser",
    "roles/storage.objectAdmin",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.ml_trainer_sa.email}"
}

# ML Server service account permissions
resource "google_project_iam_member" "ml_server_sa_roles" {
  for_each = toset([
    "roles/storage.objectViewer",
    "roles/bigquery.dataViewer",
    "roles/bigquery.jobUser",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.ml_server_sa.email}"
}

# Custom IAM role for IoT operations
resource "google_project_iam_custom_role" "iot_operator" {
  role_id     = "iotOperator"
  title       = "IoT Operator"
  description = "Custom role for IoT system operations"
  project     = var.project_id

  permissions = [
    "pubsub.topics.get",
    "pubsub.topics.list",
    "pubsub.subscriptions.get",
    "pubsub.subscriptions.list",
    "bigquery.datasets.get",
    "bigquery.tables.get",
    "bigquery.tables.list",
    "storage.buckets.get",
    "storage.objects.get",
    "storage.objects.list",
    "monitoring.timeSeries.list",
    "logging.entries.list"
  ]
}

# Service account keys (for local development)
resource "google_service_account_key" "iot_main_sa_key" {
  service_account_id = google_service_account.iot_main_sa.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# Store service account key in local file (for development only)
resource "local_file" "iot_main_sa_key_file" {
  content  = base64decode(google_service_account_key.iot_main_sa_key.private_key)
  filename = "../simulator/credentials.json"
  
  # Set restrictive permissions
  file_permission = "0600"
}

# IAM policy for Pub/Sub topic
resource "google_pubsub_topic_iam_binding" "iot_data_topic_publisher" {
  topic   = google_pubsub_topic.iot_data_topic.name
  role    = "roles/pubsub.publisher"
  project = var.project_id

  members = [
    "serviceAccount:${google_service_account.iot_simulator_sa.email}",
    "serviceAccount:${google_service_account.iot_main_sa.email}"
  ]
}

# IAM policy for Pub/Sub subscription
resource "google_pubsub_subscription_iam_binding" "iot_data_subscription_subscriber" {
  subscription = google_pubsub_subscription.iot_data_subscription.name
  role         = "roles/pubsub.subscriber"
  project      = var.project_id

  members = [
    "serviceAccount:${google_service_account.data_consumer_sa.email}",
    "serviceAccount:${google_service_account.iot_main_sa.email}"
  ]
}

# IAM policy for BigQuery dataset
resource "google_bigquery_dataset_iam_binding" "iot_dataset_editor" {
  dataset_id = google_bigquery_dataset.iot_dataset.dataset_id
  role       = "roles/bigquery.dataEditor"
  project    = var.project_id

  members = [
    "serviceAccount:${google_service_account.data_consumer_sa.email}",
    "serviceAccount:${google_service_account.iot_main_sa.email}"
  ]
}

# IAM policy for ML models bucket
resource "google_storage_bucket_iam_binding" "ml_models_bucket_admin" {
  bucket = google_storage_bucket.ml_models_bucket.name

  role = "roles/storage.objectAdmin"

  members = [
    "serviceAccount:${google_service_account.ml_trainer_sa.email}",
    "serviceAccount:${google_service_account.ml_server_sa.email}",
    "serviceAccount:${google_service_account.iot_main_sa.email}"
  ]
}