#!/bin/bash

# Apply Tekton pipeline resources to Kubernetes cluster
# This script applies all the Tekton resources in the correct order

set -e

# Function to display usage information
usage() {
  echo "Usage: $0 [OPTIONS]"
  echo "Options:"
  echo "  --registry-server <server>   Docker registry server (required for registry setup)"
  echo "  --registry-username <user>   Docker registry username (required for registry setup)"
  echo "  --registry-password <pass>   Docker registry password (required for registry setup)"
  echo "  --registry-email <email>     Docker registry email (required for registry setup)"
  echo "  --skip-registry-setup        Skip Docker registry credentials setup"
  echo "  --help                       Display this help message"
  exit 1
}

# Default values
SKIP_REGISTRY_SETUP=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --registry-server)
      REGISTRY_SERVER="$2"
      shift 2
      ;;
    --registry-username)
      REGISTRY_USERNAME="$2"
      shift 2
      ;;
    --registry-password)
      REGISTRY_PASSWORD="$2"
      shift 2
      ;;
    --registry-email)
      REGISTRY_EMAIL="$2"
      shift 2
      ;;
    --skip-registry-setup)
      SKIP_REGISTRY_SETUP=true
      shift
      ;;
    --help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

# Check if registry setup is required but parameters are missing
if [[ "$SKIP_REGISTRY_SETUP" == "false" ]]; then
  if [[ -z "$REGISTRY_SERVER" || -z "$REGISTRY_USERNAME" || -z "$REGISTRY_PASSWORD" || -z "$REGISTRY_EMAIL" ]]; then
    echo "Error: Docker registry credentials are required unless --skip-registry-setup is specified."
    usage
  fi
fi

# Set up Docker registry credentials if not skipped
if [[ "$SKIP_REGISTRY_SETUP" == "false" ]]; then
  echo "Setting up Docker registry credentials..."
  
  # Create Docker registry secret
  kubectl create secret docker-registry docker-credentials \
    --docker-server="$REGISTRY_SERVER" \
    --docker-username="$REGISTRY_USERNAME" \
    --docker-password="$REGISTRY_PASSWORD" \
    --docker-email="$REGISTRY_EMAIL" \
    --dry-run=client -o yaml | kubectl apply -f -
  
  # Create service account for Tekton
  kubectl create serviceaccount tekton-pipeline-sa --dry-run=client -o yaml | kubectl apply -f -
  
  # Add Docker credentials to service account
  kubectl patch serviceaccount tekton-pipeline-sa \
    -p '{"secrets": [{"name": "docker-credentials"}]}' \
    --type=merge
  
  echo "Docker registry credentials setup completed."
fi

echo "Creating Tekton tasks..."
kubectl apply -f tasks/lint-task.yaml
kubectl apply -f tasks/test-task.yaml
kubectl apply -f tasks/build-image-task.yaml
kubectl apply -f tasks/deploy-task.yaml
kubectl apply -f tasks/bdd-test-task.yaml

echo "Creating Tekton pipeline..."
kubectl apply -f pipeline.yaml

echo "Creating workspace PVC..."
kubectl apply -f workspace-pvc.yaml

echo "All resources applied successfully!"
echo ""
echo "To run the pipeline, update the pipeline-run.yaml with your specific parameters and run:"
echo "kubectl apply -f pipeline-run.yaml"
echo ""
echo "To monitor the pipeline execution, run:"
echo "kubectl get pipelineruns"
echo "tkn pipelinerun logs microservice-pipeline-run -f"
