# Tekton CI/CD Pipeline for Microservice

This project includes a Tekton pipeline for automating the CI/CD process of the microservice. The pipeline is designed to lint, test, build, deploy, and run BDD tests on the application.

## What is Tekton?

Tekton is a powerful and flexible open-source framework for creating CI/CD systems. It allows you to build, test, and deploy across multiple cloud providers or on-premises systems by abstracting away the underlying implementation details.

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
├── tasks/                     # Task definitions
├── pipeline/                  # Pipeline and PipelineRun definitions
├── apply-tekton-resources.sh  # Script to apply all Tekton resources
├── run-pipeline.sh            # Script to run the pipeline
└── README.md                  # Detailed documentation
```

## Getting Started

### Prerequisites

Before using this pipeline, ensure you have:

1. A Kubernetes cluster with Tekton installed
2. A container registry accessible from the cluster
3. Proper permissions to create and manage Kubernetes resources
4. kubectl installed and configured to access your cluster

### Installation

To install all Tekton resources, run:

```bash
cd tekton
./apply-tekton-resources.sh
```

### Running the Pipeline

To run the pipeline, execute:

```bash
cd tekton
./run-pipeline.sh
```

## Customization

You can customize the pipeline by modifying the YAML files in the `tekton/tasks/` and `tekton/pipeline/` directories. See the detailed documentation in `tekton/README.md` for more information.

## Detailed Documentation

For more detailed information about the pipeline, including manual installation and execution instructions, see the [Tekton README](tekton/README.md).
