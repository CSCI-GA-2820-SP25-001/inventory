#!/bin/bash

# Script to apply all Tekton resources to a Kubernetes cluster

set -e

# Print section header
print_header() {
  echo "============================================"
  echo "$1"
  echo "============================================"
}

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
  echo "Error: kubectl is not installed. Please install kubectl first."
  exit 1
fi

# Check if the user is connected to a Kubernetes cluster
if ! kubectl cluster-info &> /dev/null; then
  echo "Error: Not connected to a Kubernetes cluster. Please configure kubectl."
  exit 1
fi

# Check if Tekton is installed
if ! kubectl get crd tasks.tekton.dev &> /dev/null; then
  print_header "Tekton CRDs not found. Installing Tekton Pipelines..."
  kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml
  
  # Wait for Tekton to be ready
  echo "Waiting for Tekton to be ready..."
  kubectl wait --for=condition=established --timeout=60s crd/tasks.tekton.dev
  kubectl wait --for=condition=available --timeout=60s -n tekton-pipelines deployment/tekton-pipelines-controller
else
  echo "Tekton Pipelines already installed."
fi

# Create namespace if it doesn't exist
NAMESPACE="default"
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
  print_header "Creating namespace $NAMESPACE..."
  kubectl create namespace $NAMESPACE
fi

# Apply PersistentVolumeClaim
print_header "Applying PersistentVolumeClaim..."
kubectl apply -f pipeline/ci-cd-workspace-pvc.yaml -n $NAMESPACE

# Apply Task definitions
print_header "Applying Task definitions..."
kubectl apply -f tasks/ -n $NAMESPACE

# Apply Pipeline definition
print_header "Applying Pipeline definition..."
kubectl apply -f pipeline/ci-cd-pipeline.yaml -n $NAMESPACE

print_header "All Tekton resources applied successfully!"
echo ""
echo "To run the pipeline, apply the PipelineRun:"
echo "kubectl apply -f pipeline/ci-cd-pipeline-run.yaml -n $NAMESPACE"
echo ""
echo "To monitor the pipeline execution:"
echo "kubectl get pipelineruns -n $NAMESPACE"
echo "kubectl describe pipelinerun ci-cd-pipeline-run -n $NAMESPACE"
