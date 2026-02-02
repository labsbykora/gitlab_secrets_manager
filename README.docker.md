# Docker Usage Guide

This guide explains how to use the GitLab Secrets Manager Docker image from GitHub Container Registry.

## Quick Start

### Pull the Image

```bash
# Pull the latest image from GitHub Container Registry
docker pull ghcr.io/labsbykora/gitlab_secrets_manager:latest

# Or use a specific version tag
docker pull ghcr.io/labsbykora/gitlab_secrets_manager:v1.0.0
```

### Image Location

The image is available at:
- **Registry**: `ghcr.io`
- **Image**: `labsbykora/gitlab_secrets_manager`
- **Tags**: `latest`, `v1.0.0`, or branch names

## Prerequisites

### 1. Create Environment File

Create a `.env` file in your working directory:

```bash
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your_personal_access_token
GITLAB_PROJECT_ID=your_project_id
```

**Note**: `GITLAB_URL` is optional and defaults to `https://gitlab.com` if not specified.

### 2. Get Your GitLab Token

1. Go to your GitLab profile: `Settings > Access Tokens`
2. Create a new personal access token with `api` scope
3. Copy the token to your `.env` file

### 3. Get Your Project ID

Find your project ID in GitLab project settings under "General" or check the URL when viewing your project.

## Basic Usage

### List All Secrets

```bash
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  list
```

### Show Help

```bash
docker run --rm \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  --help
```

## Create Operations

### Create a Single Secret

```bash
# Basic create
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  create API_KEY "secret123"

# With protection options
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  create API_KEY "secret123" --protected --masked --raw

# With environment scope
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  create API_KEY "secret123" --environment-scope production

# Upsert mode (create if new, update if exists)
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  create API_KEY "secret123" --upsert
```

### Bulk Create from File

First, create your variables file (YAML, JSON, or .env format):

**YAML format** (`variables.yaml`):
```yaml
variables:
  - key: API_KEY
    value: secret123
    protected: true
    masked: true
  - key: DATABASE_URL
    value: postgresql://localhost/db
```

**JSON format** (`variables.json`):
```json
{
  "variables": [
    {
      "key": "API_KEY",
      "value": "secret123",
      "protected": true,
      "masked": true
    },
    {
      "key": "DATABASE_URL",
      "value": "postgresql://localhost/db"
    }
  ]
}
```

**ENV format** (`variables.env`):
```env
API_KEY=secret123
DATABASE_URL=postgresql://localhost/db
```

Then run:

```bash
# Create data directory and copy your file
mkdir -p data
cp variables.yaml data/

# Bulk create from YAML
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  create --file /app/data/variables.yaml

# Bulk create from JSON
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  create --file /app/data/variables.json

# Bulk create from .env file
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  create --file /app/data/variables.env

# Bulk create with upsert (updates existing variables)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  create --file /app/data/variables.yaml --upsert
```

## Read Operations

### Read a Single Secret

```bash
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  read API_KEY
```

## Update Operations

### Update a Single Secret

```bash
# Update value only
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  update API_KEY "new_secret_value"

# Update value and properties
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  update API_KEY "new_value" --protected true --masked false

# Update environment scope
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  update API_KEY "new_value" --environment-scope staging
```

### Bulk Update from File

```bash
# Create updates file (same format as create)
# Then run:
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  update --file /app/data/updates.yaml
```

## Delete Operations

### Delete a Secret

```bash
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  delete API_KEY
```

**Note**: The delete command will prompt for confirmation. To run non-interactively, you may need to pipe input:

```bash
echo "y" | docker run --rm -i \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  delete API_KEY
```

## List Operations

### List All Secrets

```bash
# Basic list (sorted by key, default)
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  list

# Sort by different fields
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  list --sort protected

docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  list --sort masked --reverse

# Show values (⚠️ use with caution for sensitive data)
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  list --show-values

# Filter by key pattern (regex supported)
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  list --filter "API.*"

docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  list --filter "DATABASE_" --show-values

docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  list --filter "^DB_" --sort key
```

## Download Operations

### Download All Secrets

**⚠️ Important**: When downloading files, you **must** mount a volume and specify `--output /app/data/filename` to save files to your host. Files saved to `/app` (the default location) will be lost when the container exits.

```bash
# Create data directory for output
mkdir -p data

# Download as YAML (simple format, default)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --output /app/data/secrets.yaml

# Download as YAML (structured format with metadata)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --structured --output /app/data/secrets.yaml

# Download as JSON (format auto-detected from .json extension)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --output /app/data/secrets.json

# Download as .env file (format auto-detected from .env extension)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --output /app/data/secrets.env

# Download with values included (⚠️ use with caution)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --include-values --output /app/data/secrets.json

# Download with custom sorting
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --sort protected --reverse --output /app/data/secrets.yaml

# Download filtered variables only
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --filter "API.*" --output /app/data/api-vars.yaml

docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --filter "DATABASE_" --include-values --output /app/data/db-vars.json
```

## Compare Operations

### Compare Local File with GitLab Variables

```bash
# Compare file with GitLab variables (shows differences)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  compare /app/data/variables.yaml

# Compare with values shown (⚠️ use with caution)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  compare /app/data/variables.yaml --show-values

# Compare showing property differences (protected/masked/raw/environment_scope)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  compare /app/data/variables.yaml --show-properties

# Show only differences (hide identical variables)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  compare /app/data/variables.yaml --only-differences

# Export comparison results to file
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  compare /app/data/variables.yaml --output /app/data/comparison.json
```

## Using Docker Compose

### Setup

1. Create or update your `.env` file with GitLab credentials:
```bash
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=your_personal_access_token
GITLAB_PROJECT_ID=your_project_id
```

2. Update `docker-compose.yml` to use the published image:

```yaml
services:
  gitlab-secrets:
    image: ghcr.io/labsbykora/gitlab_secrets_manager:latest
    container_name: gitlab-secrets-manager
    environment:
      - GITLAB_URL=${GITLAB_URL:-https://gitlab.com}
      - GITLAB_TOKEN=${GITLAB_TOKEN}
      - GITLAB_PROJECT_ID=${GITLAB_PROJECT_ID}
    volumes:
      - ./data:/app/data:rw
    stdin_open: true
    tty: true
```

### Usage Examples

```bash
# List all variables
docker-compose run --rm gitlab-secrets list

# Create a variable
docker-compose run --rm gitlab-secrets create API_KEY "secret123" --protected

# Update a variable
docker-compose run --rm gitlab-secrets update API_KEY "new_value"

# Read a variable
docker-compose run --rm gitlab-secrets read API_KEY

# Delete a variable
docker-compose run --rm gitlab-secrets delete API_KEY

# Bulk create from file
docker-compose run --rm gitlab-secrets create --file /app/data/variables.yaml

# Bulk update from file
docker-compose run --rm gitlab-secrets update --file /app/data/updates.yaml

# Download secrets (⚠️ must use /app/data/filename)
docker-compose run --rm gitlab-secrets download --output /app/data/secrets.json --include-values

# Download as YAML
docker-compose run --rm gitlab-secrets download --output /app/data/secrets.yaml --include-values

# List with filters
docker-compose run --rm gitlab-secrets list --filter "API.*" --show-values

# Compare file with GitLab
docker-compose run --rm gitlab-secrets compare /app/data/variables.yaml --only-differences
```

**⚠️ Important**: When downloading files with Docker Compose, always specify `--output /app/data/filename` to save to the mounted volume. Files saved to the default location will be lost when the container exits.

## Environment Variables

The container requires the following environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITLAB_URL` | No | `https://gitlab.com` | GitLab instance URL |
| `GITLAB_TOKEN` | Yes | - | GitLab personal access token with `api` scope |
| `GITLAB_PROJECT_ID` | Yes | - | GitLab project ID or path |

### Passing Environment Variables

**Option 1: Using `--env-file` (Recommended)**
```bash
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  list
```

**Option 2: Using `-e` flags**
```bash
docker run --rm \
  -e GITLAB_TOKEN="your_token" \
  -e GITLAB_PROJECT_ID="your_project_id" \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  list
```

**Option 3: Using environment variables from host**
```bash
export GITLAB_TOKEN="your_token"
export GITLAB_PROJECT_ID="your_project_id"

docker run --rm \
  -e GITLAB_TOKEN \
  -e GITLAB_PROJECT_ID \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  list
```

## Volume Mounts

### Mount Types

- **Read-only mount** (`:ro`): For input files (YAML, JSON, .env files for bulk operations)
- **Read-write mount** (`:rw`): For output files (downloads, comparison exports)

### Volume Mount Examples

```bash
# Create data directory
mkdir -p data

# Mount for input files (read-only)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  create --file /app/data/variables.yaml

# Mount for output files (read-write)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --output /app/data/secrets.json

# Mount for both input and output
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  compare /app/data/variables.yaml --output /app/data/comparison.json
```

## Complete Workflow Examples

### Example 1: Backup and Restore

```bash
# Create data directory
mkdir -p data

# 1. Download all secrets as backup
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --include-values --output /app/data/backup.json

# 2. Later, restore from backup
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  create --file /app/data/backup.json --upsert
```

### Example 2: Sync Variables Between Environments

```bash
# 1. Download from source environment
docker run --rm \
  --env-file .env.source \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --include-values --output /app/data/source-vars.json

# 2. Apply to target environment
docker run --rm \
  --env-file .env.target \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  create --file /app/data/source-vars.json --upsert
```

### Example 3: Bulk Update from File

```bash
# 1. Create updates file
cat > data/updates.yaml <<EOF
variables:
  - key: API_KEY
    value: new_secret_value
    protected: true
  - key: DATABASE_URL
    value: postgresql://newhost/db
EOF

# 2. Apply updates
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  update --file /app/data/updates.yaml
```

### Example 4: Compare and Sync

```bash
# 1. Download current state
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --include-values --output /app/data/current.json

# 2. Compare with desired state
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  compare /app/data/desired.yaml --only-differences --output /app/data/diff.json

# 3. Apply desired state (upsert mode updates existing, creates new)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:ro \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  create --file /app/data/desired.yaml --upsert
```

## Command Reference

### Available Commands

| Command | Description |
|---------|-------------|
| `create KEY VALUE` | Create a new secret |
| `read KEY` | Read a secret |
| `update KEY VALUE` | Update a secret |
| `delete KEY` | Delete a secret |
| `list` | List all secrets |
| `download` | Download all secrets |
| `compare FILE` | Compare local file with GitLab variables |

### Create Options

- `--protected` - Mark variable as protected
- `--masked` - Mask variable in job logs
- `--raw` - Treat variable as raw (no expansion)
- `--environment-scope SCOPE` - Environment scope (default: `*` for all environments)
- `--file` / `-f` - Bulk create from file (YAML, JSON, or .env format)
- `--upsert` - Create if new, update if already exists (no error on conflict)

### Update Options

- `--protected BOOL` - Set protected status (`true`/`false`)
- `--masked BOOL` - Set masked status (`true`/`false`)
- `--raw BOOL` - Set raw status (`true`/`false`)
- `--environment-scope SCOPE` - Set environment scope (e.g., `production`, `staging`, `*`)
- `--file` / `-f` - Bulk update from file (YAML, JSON, or .env format)

### List Options

- `--sort FIELD` - Sort by field (`key`, `protected`, `masked`, `raw`)
- `--reverse` - Reverse sort order
- `--show-values` - Display variable values (⚠️ use with caution for sensitive data)
- `--filter PATTERN` / `-f PATTERN` - Filter variables by key pattern (regex supported)

### Download Options

- `--output FILE` / `-o FILE` - Output file path (format inferred from extension if present)
- `--format FORMAT` - Output format (`yaml`, `json`, `env`) - default: inferred from file extension
- `--simple` - Use simple YAML format (key-value pairs, default for YAML)
- `--structured` - Use structured YAML format (with metadata)
- `--sort FIELD` - Sort by field (`key`, `protected`, `masked`, `raw`)
- `--reverse` - Reverse sort order
- `--include-values` - Include variable values in output (⚠️ use with caution)
- `--filter PATTERN` / `-f PATTERN` - Filter variables by key pattern (regex supported)

### Compare Options

- `--show-values` - Show variable values in comparison (⚠️ use with caution)
- `--show-properties` - Show protected/masked/raw/environment_scope differences
- `--only-differences` - Show only variables with differences (hide identical ones)
- `--output FILE` / `-o FILE` - Export comparison results to file (JSON or YAML)

## Troubleshooting

### Permission Issues with Mounted Volumes

If you encounter permission issues with mounted volumes:

```bash
# Ensure directory has proper permissions
chmod 755 data

# Or run with specific user ID (if needed)
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  --user $(id -u):$(id -g) \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --output /app/data/secrets.json
```

### Environment Variables Not Working

Verify environment variables are set correctly:

```bash
# Test with explicit environment variables
docker run --rm \
  -e GITLAB_TOKEN="your_token" \
  -e GITLAB_PROJECT_ID="your_project_id" \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  list
```

### Files Not Persisting After Container Exit

**Problem**: Files saved to `/app` are lost when container exits.

**Solution**: Always mount a volume and use `--output /app/data/filename`:

```bash
# ❌ Wrong - file will be lost
docker run --rm \
  --env-file .env \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --output secrets.json

# ✅ Correct - file persists on host
mkdir -p data
docker run --rm \
  --env-file .env \
  -v $(pwd)/data:/app/data:rw \
  ghcr.io/labsbykora/gitlab_secrets_manager:latest \
  download --output /app/data/secrets.json
```

### Authentication Errors

- Verify your `GITLAB_TOKEN` is correct and has the `api` scope
- Check that your token hasn't expired
- Ensure `GITLAB_URL` is correct if using self-hosted GitLab

### Project Not Found

- Verify your `GITLAB_PROJECT_ID` is correct
- Ensure your token has access to the project
- For self-hosted GitLab, check the project path format

### Common HTTP Status Codes

| Status Code | Meaning | Solution |
|-------------|---------|----------|
| 400 Bad Request | Invalid variable key or value | Check key/value format |
| 401 Unauthorized | Invalid or expired token | Regenerate GitLab token |
| 403 Forbidden | Permission denied | Check token has `api` scope |
| 404 Not Found | Variable or project doesn't exist | Verify variable key or project ID |
| 409 Conflict | Variable already exists (create) | Use `update` command or `--upsert` flag |
| 422 Unprocessable Entity | Validation failed | Check masked values are at least 8 characters |

## Security Best Practices

1. **Never commit `.env` files** - Keep them in `.gitignore`
2. **Use protected variables** - Mark sensitive secrets as protected
3. **Mask sensitive values** - Use `--masked` flag for secrets shown in logs
4. **Limit token scope** - Only grant `api` scope, not full access
5. **Rotate tokens regularly** - Update tokens periodically
6. **Use read-only mounts** - Mount input files as read-only when possible
7. **Be cautious with `--include-values`** - Only use when necessary
8. **Clean up downloaded files** - Remove files containing secrets after use

## Image Details

- **Base Image**: `python:3.12-slim`
- **Working Directory**: `/app`
- **User**: `appuser` (non-root, UID 1000)
- **Entrypoint**: `gitlab-secrets`
- **Default Command**: `--help`

## Additional Resources

- [Main README](README.md) - Full documentation and examples
- [Quick Start Guide](QUICKSTART.md) - Quick start instructions
- [GitHub Container Registry](https://github.com/labsbykora/gitlab_secrets_manager/pkgs/container/gitlab_secrets_manager) - Image registry
