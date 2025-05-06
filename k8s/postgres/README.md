# PostgreSQL StatefulSet for Inventory Service

This directory contains Kubernetes manifests for deploying PostgreSQL as a StatefulSet with persistent storage for the inventory service.

## Components

1. **PersistentVolume** (`pv.yaml`): Defines a persistent volume for PostgreSQL data.
2. **PersistentVolumeClaim** (`pvc.yaml`): Claims storage from the persistent volume.
3. **Secret** (`secret.yaml`): Contains PostgreSQL credentials and database URI.
4. **Service** (`service.yaml`): ClusterIP service for PostgreSQL.
5. **StatefulSet** (`statefulset.yaml`): Deploys PostgreSQL with persistent storage.

## Deployment

Apply the manifests in the following order:

```bash
# Create the PersistentVolume
kubectl apply -f pv.yaml

# Create the PersistentVolumeClaim
kubectl apply -f pvc.yaml

# Create the Secret
kubectl apply -f secret.yaml

# Create the Service
kubectl apply -f service.yaml

# Create the StatefulSet
kubectl apply -f statefulset.yaml
```

## Verification

Verify that the PostgreSQL StatefulSet is running:

```bash
# Check the StatefulSet
kubectl get statefulsets

# Check the Pods
kubectl get pods -l app=postgres

# Check the PersistentVolumes
kubectl get pv

# Check the PersistentVolumeClaims
kubectl get pvc
```

## Connecting to PostgreSQL

The PostgreSQL database can be accessed within the Kubernetes cluster using the following connection details:

- Host: `postgres`
- Port: `5432`
- Database: `postgres`
- Username: `postgres`
- Password: `postgres`

Example connection string for the inventory service:
```
postgresql+psycopg://postgres:postgres@postgres:5432/postgres
```

## Persistent Storage

The PostgreSQL deployment uses a dedicated PersistentVolume and PersistentVolumeClaim to provide persistent storage for the database. This ensures that the data survives pod restarts and rescheduling.

The PersistentVolume is configured with:
- 1Gi of storage capacity
- ReadWriteOnce access mode
- Recycle reclaim policy
- hostPath storage at `/data/postgres-data`

The PersistentVolumeClaim requests 1Gi of storage with ReadWriteOnce access mode, which is bound to the PersistentVolume.

## Updating the Deployment

To update the PostgreSQL deployment (e.g., after changing configuration), simply apply the manifests again:

```bash
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
kubectl apply -f secret.yaml
kubectl apply -f service.yaml
kubectl apply -f statefulset.yaml
```

Or apply all manifests at once:

```bash
kubectl apply -f .
```

## Updating Application Configuration

To update the application's configuration to use the PostgreSQL service in Kubernetes, you'll need to set the DATABASE_URI environment variable in your application to:

```
postgresql+psycopg://postgres:postgres@postgres:5432/postgres
```

This can be done by updating your application's environment variables or configuration files.

## Cleaning Up

To clean up the PostgreSQL deployment, delete the resources in the reverse order:

```bash
kubectl delete -f statefulset.yaml
kubectl delete -f service.yaml
kubectl delete -f secret.yaml
kubectl delete -f pvc.yaml
kubectl delete -f pv.yaml
```

Or delete all resources at once:

```bash
kubectl delete -f .
```

Note: If you want to preserve your data, you should back it up before cleaning up.
