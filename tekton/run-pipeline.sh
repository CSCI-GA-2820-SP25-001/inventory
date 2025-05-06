#!/bin/bash

# Script to run the Tekton pipeline and monitor its execution

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

# Set namespace
NAMESPACE="default"

# Check if the pipeline exists
if ! kubectl get pipeline ci-cd-pipeline -n $NAMESPACE &> /dev/null; then
  echo "Error: Pipeline 'ci-cd-pipeline' not found in namespace '$NAMESPACE'."
  echo "Please run the apply-tekton-resources.sh script first."
  exit 1
fi

# Generate a unique name for the PipelineRun
TIMESTAMP=$(date +%Y%m%d%H%M%S)
PIPELINERUN_NAME="ci-cd-pipeline-run-$TIMESTAMP"

# Create a copy of the PipelineRun with the unique name
print_header "Creating PipelineRun $PIPELINERUN_NAME..."
sed "s/ci-cd-pipeline-run/$PIPELINERUN_NAME/g" pipeline/ci-cd-pipeline-run.yaml > pipeline/temp-pipeline-run.yaml

# Apply the PipelineRun
kubectl apply -f pipeline/temp-pipeline-run.yaml -n $NAMESPACE

# Clean up the temporary file
rm pipeline/temp-pipeline-run.yaml

print_header "PipelineRun $PIPELINERUN_NAME started!"
echo ""
echo "To monitor the pipeline execution:"
echo "kubectl get pipelineruns $PIPELINERUN_NAME -n $NAMESPACE"
echo "kubectl describe pipelinerun $PIPELINERUN_NAME -n $NAMESPACE"
echo ""

# Ask if the user wants to monitor the pipeline execution
read -p "Do you want to monitor the pipeline execution? (y/n): " MONITOR
if [[ $MONITOR == "y" || $MONITOR == "Y" ]]; then
  print_header "Monitoring PipelineRun $PIPELINERUN_NAME..."
  
  # Wait for the PipelineRun to complete
  echo "Waiting for PipelineRun to complete..."
  kubectl wait --for=condition=succeeded --timeout=1800s pipelinerun/$PIPELINERUN_NAME -n $NAMESPACE || true
  
  # Get the status of the PipelineRun
  STATUS=$(kubectl get pipelinerun $PIPELINERUN_NAME -n $NAMESPACE -o jsonpath='{.status.conditions[0].reason}')
  
  if [[ $STATUS == "Succeeded" ]]; then
    print_header "PipelineRun $PIPELINERUN_NAME completed successfully!"
  else
    print_header "PipelineRun $PIPELINERUN_NAME failed or timed out."
    echo "Check the logs for more details:"
    echo "kubectl logs -l tekton.dev/pipelineRun=$PIPELINERUN_NAME -n $NAMESPACE"
  fi
fi
