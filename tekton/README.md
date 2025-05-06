# Tekton CI/CD Pipeline for Microservice

This directory contains Tekton pipeline definitions for automating the CI/CD process of the microservice.

## Pipeline Overview

The pipeline automates the following steps:

1. **Lint**: Runs code linting using flake8 and pylint
2. **Test**: Runs unit tests using pytest
3. **Build**: Builds a Docker image and pushes it to a registry
4. **Deploy**: Deploys the application to Kubernetes
5. **BDD Tests**: Runs behavior-driven development tests against the deployed application

## Directory Structure

```
tekton/
├── tasks/
│   ├── lint-task.yaml         # Task for linting the code
│   ├── test-task.yaml         # Task for running unit tests
│   ├── build-task.yaml        # Task for building and pushing Docker image
│   ├── deploy-task.yaml       # Task for deploying to Kubernetes
│   └── bdd-test-task.yaml     # Task for running BDD tests
├── pipeline/
│   ├── ci-cd-pipeline.yaml           # Pipeline definition
│   ├── ci-cd-pipeline-run.yaml       # PipelineRun to trigger the pipeline
│   └── ci-cd-workspace-pvc.yaml      # PersistentVolumeClaim for the pipeline
└── README.md                  # This file
```

## Prerequisites

Before using this pipeline, ensure you have:

1. A Kubernetes cluster with Tekton installed
2. A container registry accessible from the cluster
3. Proper permissions to create and manage Kubernetes resources

## Installation

### Using the provided script

The easiest way to install all Tekton resources is to use the provided script:

```bash
./apply-tekton-resources.sh
```

This script will:
1. Check if Tekton is installed and install it if necessary
2. Apply the PersistentVolumeClaim
3. Apply all Task definitions
4. Apply the Pipeline definition

### Manual installation

If you prefer to install the resources manually:

1. Apply the PersistentVolumeClaim:

```bash
kubectl apply -f tekton/pipeline/ci-cd-workspace-pvc.yaml
```

2. Apply the Task definitions:

```bash
kubectl apply -f tekton/tasks/
```

3. Apply the Pipeline definition:

```bash
kubectl apply -f tekton/pipeline/ci-cd-pipeline.yaml
```

## Usage

### Using the provided script

The easiest way to run the pipeline is to use the provided script:

```bash
./run-pipeline.sh
```

This script will:
1. Create a PipelineRun with a unique name
2. Apply the PipelineRun to the cluster
3. Optionally monitor the pipeline execution

### Manual execution

If you prefer to run the pipeline manually:

```bash
kubectl apply -f tekton/pipeline/ci-cd-pipeline-run.yaml
```

You can customize the parameters in the PipelineRun file before applying it:

- `image-name`: The name of the Docker image
- `image-tag`: The tag of the Docker image
- `registry`: The container registry to push the image to
- `namespace`: The Kubernetes namespace to deploy to
- `app-url`: The URL of the deployed application for BDD tests

## Monitoring

You can monitor the pipeline execution using the Tekton Dashboard or with kubectl:

```bash
# List PipelineRuns
kubectl get pipelineruns

# Get details of a specific PipelineRun
kubectl describe pipelinerun ci-cd-pipeline-run

# Get logs of a specific TaskRun
kubectl logs -l tekton.dev/pipelineRun=ci-cd-pipeline-run -f
```

## Customization

You can customize the pipeline by:

1. Modifying the Task definitions in the `tasks/` directory
2. Updating the Pipeline definition in `pipeline/ci-cd-pipeline.yaml`
3. Creating a new PipelineRun with different parameters
