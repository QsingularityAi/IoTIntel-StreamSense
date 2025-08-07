# Terraform Infrastructure for IoT Anomaly Detection System

This directory contains Terraform configuration files to deploy the complete infrastructure for the IoT Anomaly Detection System on Google Cloud Platform.

## 🏗️ Infrastructure Components

### Core Resources
- **Pub/Sub**: Topics and subscriptions for real-time data streaming
- **BigQuery**: Data warehouse with partitioned tables for sensor data and ML predictions
- **Cloud Storage**: Buckets for ML models and data backups
- **IAM**: Service accounts and permissions for secure access
- **Monitoring**: Dashboards, alerts, and logging configuration

### Optional Resources
- **VPC Network**: Custom networking for compute instances
- **Compute Engine**: VM instances for processing (if enabled)
- **GKE Cluster**: Kubernetes cluster for container orchestration (if enabled)
- **Budget Alerts**: Cost management and monitoring

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install Terraform
brew install terraform  # macOS
# or
sudo apt-get install terraform  # Ubuntu

# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

### 2. Setup Authentication
```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 3. Configure Variables
```bash
# Copy example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
vim terraform.tfvars
```

### 4. Deploy Infrastructure
```bash
# Initialize Terraform
terraform init

# Review planned changes
terraform plan -var="project_id=YOUR_PROJECT_ID"

# Apply changes
terraform apply -var="project_id=YOUR_PROJECT_ID"
```

## 📁 File Structure

```
terraform/
├── main.tf                 # Core infrastructure resources
├── variables.tf            # Variable definitions
├── outputs.tf             # Output values
├── iam.tf                 # IAM roles and permissions
├── monitoring.tf          # Monitoring and alerting
├── terraform.tfvars.example # Example variables file
└── README.md              # This file
```

## 🔧 Configuration Files

### main.tf
- Pub/Sub topics and subscriptions
- BigQuery datasets and tables
- Cloud Storage buckets
- Service accounts
- Network resources (optional)

### iam.tf
- Service account permissions
- IAM role bindings
- Custom IAM roles
- Resource-level access control

### monitoring.tf
- Cloud Monitoring dashboards
- Alert policies
- Log sinks
- Budget alerts
- Custom metrics

### variables.tf
- All configurable parameters
- Default values
- Variable descriptions
- Type constraints

### outputs.tf
- Resource identifiers
- Connection strings
- Service URLs
- Configuration values for Docker Compose

## 🎯 Key Variables

### Required
```hcl
project_id = "your-gcp-project-id"
```

### Common Customizations
```hcl
# Environment and region
environment = "dev"          # dev, staging, prod
region = "us-central1"

# Resource naming
pubsub_topic_name = "iot-temp-vibration-data"
bigquery_dataset_id = "iot_data"
ml_model_bucket_name = "iot-ml-models"

# Features
enable_monitoring = true
enable_compute_instances = false
enable_gke = false

# Cost management
budget_amount = 100
budget_alert_threshold = 80
```

## 📊 Outputs

After deployment, Terraform provides useful outputs:

```bash
# View all outputs
terraform output

# Specific outputs
terraform output docker_compose_env_vars
terraform output service_urls
terraform output bigquery_connection_info
```

### Key Outputs
- **docker_compose_env_vars**: Environment variables for Docker Compose
- **service_urls**: URLs for accessing deployed services
- **bigquery_connection_info**: BigQuery connection strings
- **service_account_emails**: Service account identifiers
- **quick_start_commands**: Commands to get started

## 🔒 Security Best Practices

### Service Accounts
- Minimal required permissions
- Separate service accounts for each component
- Regular key rotation

### Network Security
- Private Google access enabled
- Firewall rules for internal communication only
- VPC isolation (when compute instances enabled)

### Data Protection
- BigQuery dataset access controls
- Cloud Storage bucket permissions
- Encryption at rest and in transit

## 💰 Cost Management

### Budget Monitoring
```hcl
budget_amount = 100              # Monthly budget in USD
budget_alert_threshold = 80     # Alert at 80% of budget
```

### Cost Optimization
- BigQuery table partitioning by date
- Cloud Storage lifecycle policies
- Automatic log retention policies
- Resource labeling for cost tracking

### Estimated Costs (Monthly)
- **BigQuery**: $20-50 (depends on data volume)
- **Pub/Sub**: $5-10 (depends on message volume)
- **Cloud Storage**: $1-5 (depends on model storage)
- **Monitoring**: $0-5 (basic monitoring)
- **Total**: ~$31-85 per month

## 🔄 Lifecycle Management

### Updates
```bash
# Update infrastructure
terraform plan
terraform apply

# Update specific resources
terraform apply -target=google_bigquery_table.sensor_readings_table
```

### Destruction
```bash
# Destroy all resources (BE CAREFUL!)
terraform destroy

# Destroy specific resources
terraform destroy -target=google_compute_instance.example
```

### State Management
```bash
# View current state
terraform show

# List resources
terraform state list

# Import existing resources
terraform import google_pubsub_topic.example projects/PROJECT_ID/topics/TOPIC_NAME
```

## 🚨 Troubleshooting

### Common Issues

**1. Permission Denied**
```bash
# Ensure proper authentication
gcloud auth application-default login

# Check project permissions
gcloud projects get-iam-policy PROJECT_ID
```

**2. API Not Enabled**
```bash
# Enable required APIs
gcloud services enable pubsub.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
```

**3. Resource Already Exists**
```bash
# Import existing resource
terraform import google_pubsub_topic.iot_data_topic projects/PROJECT_ID/topics/TOPIC_NAME

# Or use different names in variables
```

**4. Billing Account Issues**
```bash
# List billing accounts
gcloud billing accounts list

# Link project to billing account
gcloud billing projects link PROJECT_ID --billing-account=BILLING_ACCOUNT_ID
```

### Validation
```bash
# Validate configuration
terraform validate

# Format configuration
terraform fmt

# Check for security issues
terraform plan | grep -i "warning\|error"
```

## 🔧 Advanced Configuration

### Remote State Backend
```hcl
terraform {
  backend "gcs" {
    bucket = "your-terraform-state-bucket"
    prefix = "iot-anomaly-detection"
  }
}
```

### Multiple Environments
```bash
# Use workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch environments
terraform workspace select dev
```

### Custom Modules
```hcl
module "iot_infrastructure" {
  source = "./modules/iot-infrastructure"
  
  project_id = var.project_id
  environment = var.environment
}
```

## 📚 Additional Resources

- [Terraform Google Provider Documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Google Cloud Architecture Center](https://cloud.google.com/architecture)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [Pub/Sub Best Practices](https://cloud.google.com/pubsub/docs/best-practices)

## 🤝 Contributing

1. Follow Terraform best practices
2. Use consistent naming conventions
3. Add appropriate labels and descriptions
4. Test changes in development environment
5. Update documentation for new resources

## 📄 License

This Terraform configuration is part of the IoT Anomaly Detection System and follows the same license terms.