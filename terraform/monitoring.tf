# Monitoring and alerting configuration for IoT Anomaly Detection System

# Log sink for IoT data pipeline
resource "google_logging_project_sink" "iot_pipeline_sink" {
  count = var.enable_monitoring ? 1 : 0

  name        = "iot-pipeline-sink"
  destination = "bigquery.googleapis.com/projects/${var.project_id}/datasets/${google_bigquery_dataset.iot_dataset.dataset_id}"
  
  # Log filter for IoT-related logs
  filter = <<-EOT
    resource.type="pubsub_topic" OR
    resource.type="bigquery_resource" OR
    resource.type="gcs_bucket" OR
    (resource.type="container" AND resource.labels.container_name=~"iot-.*")
  EOT

  # Use a unique writer identity
  unique_writer_identity = true
}

# Grant BigQuery Data Editor role to the log sink's writer identity
resource "google_project_iam_member" "log_sink_writer" {
  count = var.enable_monitoring ? 1 : 0

  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = google_logging_project_sink.iot_pipeline_sink[0].writer_identity
}

# Monitoring notification channel (email)
resource "google_monitoring_notification_channel" "email_channel" {
  count = var.enable_monitoring ? 1 : 0

  display_name = "IoT System Email Alerts"
  type         = "email"
  project      = var.project_id

  labels = {
    email_address = "admin@example.com"  # Replace with actual email
  }

  description = "Email notifications for IoT system alerts"
}

# Alert policy for high error rate in Pub/Sub
resource "google_monitoring_alert_policy" "pubsub_error_rate" {
  count = var.enable_monitoring ? 1 : 0


  display_name = "High Pub/Sub Error Rate"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "Pub/Sub error rate > 5%"

    condition_threshold {
      filter          = "resource.type=\"pubsub_subscription\" AND resource.labels.subscription_id=\"${var.pubsub_subscription_name}\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.05

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email_channel[0].name]

  alert_strategy {
    auto_close = "1800s"  # 30 minutes
  }
}

# Alert policy for BigQuery job failures
resource "google_monitoring_alert_policy" "bigquery_job_failures" {
  count = var.enable_monitoring ? 1 : 0


  display_name = "BigQuery Job Failures"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "BigQuery job failure rate > 10%"

    condition_threshold {
      filter          = "resource.type=\"bigquery_project\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.1

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email_channel[0].name]
}

# Alert policy for anomaly detection rate
resource "google_monitoring_alert_policy" "high_anomaly_rate" {
  count = var.enable_monitoring ? 1 : 0


  display_name = "High Anomaly Detection Rate"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "Anomaly rate > 20%"

    condition_threshold {
      filter          = "resource.type=\"global\""
      duration        = "600s"  # 10 minutes
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.2

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email_channel[0].name]

  alert_strategy {
    auto_close = "3600s"  # 1 hour
  }
}

# Dashboard for IoT system monitoring
resource "google_monitoring_dashboard" "iot_system_dashboard" {
  count = var.enable_monitoring ? 1 : 0

  dashboard_json = jsonencode({
    displayName = "IoT Anomaly Detection System"
    mosaicLayout = {
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Pub/Sub Message Rate"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"pubsub_topic\" AND resource.labels.topic_id=\"${var.pubsub_topic_name}\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                    }
                  }
                }
              }]
            }
          }
        },
        {
          width  = 6
          height = 4
          xPos   = 6
          widget = {
            title = "BigQuery Slot Usage"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"bigquery_project\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_MEAN"
                    }
                  }
                }
              }]
            }
          }
        },
        {
          width  = 12
          height = 4
          yPos   = 4
          widget = {
            title = "ML Prediction Metrics"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"global\" AND metric.type=\"custom.googleapis.com/iot/anomaly_rate\""
                    aggregation = {
                      alignmentPeriod  = "300s"
                      perSeriesAligner = "ALIGN_MEAN"
                    }
                  }
                }
              }]
            }
          }
        }
      ]
    }
  })
}

# Custom metric for anomaly detection rate
resource "google_monitoring_metric_descriptor" "anomaly_rate_metric" {
  count = var.enable_monitoring ? 1 : 0

  type         = "custom.googleapis.com/iot/anomaly_rate"
  metric_kind  = "GAUGE"
  value_type   = "DOUBLE"
  display_name = "IoT Anomaly Detection Rate"
  description  = "Rate of anomalies detected by ML models"
  project      = var.project_id

  labels {
    key         = "device_type"
    value_type  = "STRING"
    description = "Type of IoT device"
  }

  labels {
    key         = "building"
    value_type  = "STRING"
    description = "Building identifier"
  }
}

# Budget alert for cost management
resource "google_billing_budget" "iot_system_budget" {
  count = var.budget_amount > 0 ? 1 : 0

  billing_account = data.google_billing_account.account.id
  display_name    = "IoT System Budget"

  budget_filter {
    projects = ["projects/${var.project_id}"]
    
    services = [
      "services/95FF2659-5EA1-4CC2-9951-8A878F86C1B1",  # BigQuery
      "services/0D5D-991C-5C4D-9AB6-3A824A4C1B1F",      # Pub/Sub
      "services/5490-E99B-4C9B-9B18-7344FD842676",      # Cloud Storage
      "services/6F81-5844-456A-842A-B3A72C9B2F8A"       # Compute Engine
    ]
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = tostring(var.budget_amount)
    }
  }

  threshold_rules {
    threshold_percent = var.budget_alert_threshold / 100
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "FORECASTED_SPEND"
  }
}

# Data source for billing account
data "google_billing_account" "account" {
  display_name = "My Billing Account"  # Replace with actual billing account name
  open         = true
}