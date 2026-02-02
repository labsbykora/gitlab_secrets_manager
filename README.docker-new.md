# Docker Usage Guide

This guide explains how to use GitLab Secrets Manager with Docker.

## Building the Docker Image

```bash
# Build the image
docker build -t gitlab-secrets-manager:latest .

# Or build with a specific tag
docker build -t gitlab-secrets-manager:1.0.0 .
```

## Running with Docker

### Basic Usage

```bash
# List all variables
docker run --rm \
  -e GITLAB_TOKEN="your_token" \
  -e GITLAB_PROJECT_ID="your_project_id" \
  gitlab-secrets-manager:latest \
  list

# Create a variable
docker run --rm \
  -e GITLAB_TOKEN="your_token" \
  -e GITLAB_PROJECT_ID="your_project_id" \
  gitlab-secrets-manager:latest \
  create API_KEY "secret123" --protected

# Download variables to a file
docker run --rm \
  -e GITLAB_TOKEN="your_token" \
  -e GITLAB_PROJECT_ID="your_project_id" \
  -v $(pwd)/output:/app/data \
  gitlab-secrets-manager:latest \
  download --output /app/data/secrets.json --include-values
```

### Using Environment File

Create a `.env` file (or use your existing one):

```bash
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your_personal_access_token
GITLAB_PROJECT_ID=your_project_id
```

Run with environment file:

```bash
docker run --rm \
  --env-file .env \
  gitlab-secrets-manager:latest \
  list
```

### Mounting Volumes for File Operations

```bash
# Create a directory for input/output files
mkdir -p data

# Bulk create from a file
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  gitlab-secrets-manager:latest \
  create --file /app/data/variables.yaml

# Bulk update from a file
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  gitlab-secrets-manager:latest \
  update --file /app/data/updates.yaml

# Download to mounted volume
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  gitlab-secrets-manager:latest \
  download --output /app/data/backup.json --include-values
```

### Using Docker Compose

1. Create or update your `.env` file with your GitLab credentials:

```bash
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your_personal_access_token
GITLAB_PROJECT_ID=your_project_id
```

2. Run commands:

```bash
# List variables
docker-compose run --rm gitlab-secrets list

# Create a variable
docker-compose run --rm gitlab-secrets create API_KEY "secret123" --protected

# Download variables
# IMPORTANT: Always use --output /app/data/filename to save to the mounted volume
docker-compose run --rm gitlab-secrets download --output /app/data/secrets.json --include-values

# Or download as YAML
docker-compose run --rm gitlab-secrets download --output /app/data/secrets.yaml --include-values
```

**⚠️ Important:** When downloading files, you **must** specify `--output /app/data/filename` to save to the mounted volume. Files saved to the default location (e.g., `secrets.yml` in `/app`) will be **lost** when the container exits because `/app` is not mounted - only `/app/data` is mounted to `./data` on your host.

## Dockerfile Options

### Production Dockerfile (`Dockerfile`)

- Minimal size (Python slim image)
- Non-root user for security
- Optimized for production use

### Development Dockerfile (`Dockerfile.dev`)

- Includes development tools (git, vim, curl)
- Useful for debugging and development
- Build with: `docker build -f Dockerfile.dev -t gitlab-secrets-manager:dev .`

## Environment Variables

The container requires the following environment variables:

- `GITLAB_URL` (optional, defaults to `https://gitlab.com`)
- `GITLAB_TOKEN` (required)
- `GITLAB_PROJECT_ID` (required)

## Volume Mounts

- **Read-only mount** (`:ro`): For input files (YAML, JSON, .env)
- **Read-write mount** (`:rw`): For output files (downloads)

## Examples

### Complete Workflow Example

```bash
# 1. Create data directory
mkdir -p data

# 2. Create variables from file
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  gitlab-secrets-manager:latest \
  create --file /app/data/variables.yaml

# 3. List all variables
docker run --rm \
  --env-file .env \
  gitlab-secrets-manager:latest \
  list

# 4. Download backup
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  gitlab-secrets-manager:latest \
  download --output /app/data/backup.json --include-values
```

## Troubleshooting

### Permission Issues

If you encounter permission issues with mounted volumes, ensure the directory has proper permissions:

```bash
chmod 755 data
```

### Environment Variables Not Working

Make sure environment variables are set correctly:

```bash
docker run --rm \
  -e GITLAB_TOKEN="your_token" \
  -e GITLAB_PROJECT_ID="your_project_id" \
  gitlab-secrets-manager:latest \
  list
```
