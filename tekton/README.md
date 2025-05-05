# Tekton CI/CD Pipeline for Microservice

This directory contains Tekton pipeline definitions for automating the CI/CD process of the microservice.

## Pipeline Overview

The pipeline automates the following steps:
1. **Lint**: Runs code linting using flake8 and pylint
2. **Test**: Executes unit tests using pytest
3. **Build Docker Image**: Builds and pushes a Docker image using Kaniko
4. **Deploy**: Deploys the application to Kubernetes
5. **BDD Tests**: Runs Behavior-Driven Development tests against the deployed application

## Prerequisites

- Kubernetes cluster with Tekton installed
- kubectl configured to communicate with your cluster
- Tekton Pipelines and Tekton Dashboard installed
- git-clone ClusterTask installed (part of Tekton Catalog)
- Docker registry credentials (for pushing images)

## Installation

1. Set up Docker registry credentials:

```bash
# Create a secret with your Docker registry credentials
kubectl create secret docker-registry docker-credentials \
  --docker-server=<your-registry-server> \
  --docker-username=<your-username> \
  --docker-password=<your-password> \
  --docker-email=<your-email>

# Create a service account for Tekton to use
kubectl create serviceaccount tekton-pipeline-sa

# Add the Docker credentials to the service account
kubectl patch serviceaccount tekton-pipeline-sa \
  -p '{"secrets": [{"name": "docker-credentials"}]}'
```

2. Create the necessary tasks:

```bash
kubectl apply -f tekton/tasks/lint-task.yaml
kubectl apply -f tekton/tasks/test-task.yaml
kubectl apply -f tekton/tasks/build-image-task.yaml
kubectl apply -f tekton/tasks/deploy-task.yaml
kubectl apply -f tekton/tasks/bdd-test-task.yaml
```

3. Create the pipeline:

```bash
kubectl apply -f tekton/pipeline.yaml
```

4. Create the persistent volume claim for the workspace:

```bash
kubectl apply -f tekton/workspace-pvc.yaml
```

## Running the Pipeline

1. Update the `pipeline-run.yaml` file with your specific parameters:
   - git-url: URL of your git repository
   - image-name: Name of the Docker image to build
   - namespace: Kubernetes namespace to deploy to
   - app-name: Name of your application
   - app-url: URL where your application will be accessible

2. Run the pipeline:

```bash
kubectl apply -f tekton/pipeline-run.yaml
```

3. Monitor the pipeline execution:

```bash
kubectl get pipelineruns
tkn pipelinerun logs microservice-pipeline-run -f
```

## Pipeline Resources

- **Tasks**: Individual units of work in the pipeline
  - `lint-task.yaml`: Runs linting on the source code using flake8 and pylint
  - `test-task.yaml`: Runs unit tests using pytest and generates JUnit XML reports
  - `build-image-task.yaml`: Builds and pushes a Docker image using Kaniko with caching enabled
  - `deploy-task.yaml`: Deploys the application to Kubernetes with health checks and resource limits
  - `bdd-test-task.yaml`: Runs BDD tests against the deployed application using behave

- **Pipeline**: `pipeline.yaml` defines the execution order of tasks

- **PipelineRun**: `pipeline-run.yaml` is an example of how to instantiate and run the pipeline

- **PVC**: `workspace-pvc.yaml` defines the persistent volume claim for the shared workspace

## Task Improvements

The tasks have been enhanced with the following features:

1. **Lint Task**:
   - Improved error handling with detailed output
   - Proper exit codes for CI/CD integration

2. **Test Task**:
   - JUnit XML report generation for test results visualization
   - Proper virtual environment setup with pipenv

3. **Build Image Task**:
   - Caching enabled to speed up builds
   - Compressed caching disabled to improve reliability
   - Cleanup after build to reduce disk usage

4. **Deploy Task**:
   - Resource limits and requests for better cluster resource management
   - Health checks (readiness and liveness probes) for improved reliability
   - Namespace creation if it doesn't exist
   - Detailed deployment status information

5. **BDD Test Task**:
   - Separate smoke test run for quick feedback
   - Full test suite run for comprehensive testing
   - Improved environment variable configuration

## Customization

You can customize the pipeline by:
- Adding additional tasks
- Modifying existing tasks to fit your specific requirements
- Adjusting the pipeline parameters in the PipelineRun
- Adding additional security scanning or compliance checks

## Troubleshooting

If you encounter issues:
1. Check the logs of the specific task that failed:
   ```bash
   tkn taskrun logs <taskrun-name> -f
   ```

2. Ensure all required secrets and service accounts are properly configured:
   ```bash
   kubectl get secrets
   kubectl get serviceaccounts
   ```

3. Verify that the git repository is accessible:
   ```bash
   # Test git clone in a temporary pod
   kubectl run git-test --rm -i --tty --image=alpine/git -- clone <your-git-url>
   ```

4. Check that the Docker registry credentials are properly configured:
   ```bash
   kubectl get secret docker-credentials -o yaml
   ```

5. Verify the PVC is correctly bound:
   ```bash
   kubectl get pvc microservice-workspace-pvc
   ```

## CI/CD Integration

This Tekton pipeline can be triggered by:

1. **Webhook**: Set up a Tekton trigger to automatically start the pipeline on git push
2. **Manual**: Apply the PipelineRun manually for controlled deployments
3. **Scheduled**: Use a CronJob to trigger the pipeline at regular intervals

For webhook setup, refer to the [Tekton Triggers documentation](https://tekton.dev/docs/triggers/).
