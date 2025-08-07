FROM jupyter/base-notebook:latest

# Install additional dependencies
RUN pip install --no-cache-dir \
    google-cloud-bigquery==3.10.0 \
    pandas==1.5.3 \
    numpy==1.24.3 \
    matplotlib==3.7.1 \
    seaborn==0.12.2 \
    scikit-learn==1.3.0

# Expose port
EXPOSE 8888

# Copy notebooks directory from project root
COPY notebooks/ ./notebooks/

# Set working directory
WORKDIR /app

# Start JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
