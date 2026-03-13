# nrp-devtools Setup Documentation

This document describes what nrp-devtools does to set up and run the InvenioRDM-based computational chemistry repository.

## Location of nrp-devtools

The nrp-devtools package is located at:
```
.venv/lib/python3.13/site-packages/nrp_devtools/
```

## Main Commands

### 1. `nrp initialize` - Project Initialization

When creating a new project, `nrp initialize` does the following:

1. Creates project structure from cookiecutter template at:
   - Template location: `nrp_devtools/templates/repository/`
   - Creates: `docker/`, `{ui_package}/`, `{shared_package}/`, `{model_package}/`, `i18n/`, etc.

2. Generates self-signed SSL certificates:
   - `docker/development.crt`
   - `docker/development.key`

3. Creates symlink:
   - `docker/.env` -> `variables`

4. Makes `nrp` command executable

5. Sets up i18n configuration

---

### 2. `nrp check` - Environment Check and Fix

The `nrp check` command validates and fixes the environment. It runs these steps:

#### Infrastructure Checks
1. Check `docker/.env` file exists (create symlink if missing)
2. Docker is callable (`docker ps`)
3. Docker Compose version (expected: 1.17+)
4. Node.js version (expected: 14, 16, 20, or 21)
5. npm version (expected: 6, 7, 8, or 10)
6. ImageMagick is callable (`convert --version`)

#### Virtual Environment Checks
7. `.venv` directory exists
8. Python installation in `.venv` is functional
9. pip installation in `.venv` is functional

#### Requirements Checks
10. Check `requirements.txt` exists and is up to date
    - If missing or outdated, rebuilds requirements using:
      - `uv pip compile` to generate requirements.txt from pyproject.toml
      - Handles oarepo dependencies separately
      - Applies forks (if any) to installed packages

#### Invenio Configuration Checks
11. Check `invenio.cfg` exists in `.venv/var/instance`
12. Check `variables` file exists in `.venv/var/instance`
    - Creates symlinks if missing

#### Python Repository Checks
13. Check `invenio` command is callable in virtualenv
    - If not, installs the Python repository using the resolver

#### Local Packages
14. Install any local packages specified via `-e` flag

#### Docker Containers Checks
15. Start Docker containers if not running:
    ```bash
    docker compose up -d cache db mq search s3
    ```
16. Test container connectivity:
    - Database (PostgreSQL)
    - OpenSearch
    - S3 (MinIO)
    - Message Queue (RabbitMQ)
    - Cache (Redis)

#### UI Checks
17. Check `manifest.json` exists and is ready
    - If not, builds UI:
      - `invenio oarepo assets collect` - collects assets
      - `invenio webpack install` - installs npm packages
      - `invenio webpack build --production` - builds production UI

#### Database Checks
18. Check database status via `invenio oarepo check`
    - If `not_initialized`: runs `invenio db create`
    - If `migration_pending`: runs `invenio alembic upgrade heads`

#### OpenSearch Checks
19. Check OpenSearch is accessible and contains indices
20. Fix custom fields in OpenSearch

#### S3 Checks
21. Check S3 location exists in database
22. Check S3 bucket exists

---

### 3. `nrp build` - Production Build

The `nrp build` command creates a production-ready environment:

1. Display message: "Building repository for production"

2. Clean previous installation:
   - Removes `.venv` directory

3. Create empty virtualenv:
   - Uses `python -m venv` to create `.venv`
   - Installs setuptools, pip, wheel

4. Check and build requirements:
   - Creates temporary project directory (`.nrp/oarepo-pdm`)
   - Locks Python repository using `uv pip compile`
   - Exports requirements to `requirements.txt`
   - Resolves dependencies for oarepo separately

5. Install Python repository:
   - Uses `uv pip sync` to install resolved requirements
   - Installs project in editable mode: `uv pip install -e .`
   - Applies forks (if configured)

6. Install Invenio configuration:
   - Symlink `invenio.cfg` to instance path
   - Symlink `variables` to instance path

7. Copy translations from oarepo's `collected_translations`

8. Collect assets:
   - `invenio oarepo assets collect`
   - Creates `watch.list.json`

9. Install NPM packages:
   - `invenio webpack install`

10. Build production UI:
    - `invenio webpack build --production`
    - Modifies webpack config to disable clean plugin

---

### 4. `nrp develop` - Development Mode

The `nrp develop` command starts the development environment:

1. Run check commands (if `--checks` flag is set, which is default)
2. Copy translations to site-packages
3. Copy assets to webpack build directory
4. Start Python server in development mode:
   ```bash
   invenio run \
     --cert docker/development.crt \
     --key docker/development.key
   ```
   With environment variables:
   - `FLASK_DEBUG=1`
   - `INVENIO_TEMPLATES_AUTO_RELOAD=1`

5. Start Webpack server:
   ```bash
   npm run start
   ```
   (in `.venv/var/instance/assets`)

6. Start file watcher:
   - Watches paths from `watch.list.json`
   - Copies changed files to `.venv/var/instance/static` and `.venv/var/instance/assets`

---

### 5. `nrp run` - Run in Production

The `nrp run` command starts the repository in production mode:

1. Start Python server (without FLASK_DEBUG)
2. Start development controller

---

## Package Resolvers

nrp-devtools supports two package resolvers:

### UV Resolver (default)
- Uses `uv pip` for all Python operations
- Commands:
  - `uv pip compile pyproject.toml -o requirements.txt` - lock dependencies
  - `uv pip sync requirements.txt` - install dependencies
  - `uv pip install -e .` - install project
  - `uv pip install --force-reinstall --no-deps <packages>` - install forks

### PDM Resolver (when `NRP_USE_PDM=1`)
- Uses PDM for dependency management
- Similar workflow but with PDM commands

---

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `.venv/` | Python virtual environment |
| `.venv/var/instance/` | Invenio instance path |
| `.venv/var/instance/assets/` | Webpack assets directory |
| `.venv/var/instance/static/` | Static files directory |
| `.venv/var/instance/webpack-config.json` | Webpack configuration |
| `docker/.env` | Symlink to `variables` file |
| `docker/development.crt` | SSL certificate for dev |
| `docker/development.key` | SSL key for dev |
| `oarepo.yaml` | Project configuration |

---

## Environment Variables

nrp-devtools sets these environment variables globally:
- `PIP_EXTRA_INDEX_URL=https://gitlab.cesnet.cz/api/v4/projects/1408/packages/pypi/simple`
- `UV_EXTRA_INDEX_URL=https://gitlab.cesnet.cz/api/v4/projects/1408/packages/pypi/simple`

The Invenio command uses:
- `INVENIO_INSTANCE_PATH` - Path to `.venv/var/instance`
- `FLASK_DEBUG` - Set to "1" in development mode

---

## Setup Flow Summary

```
1. nrp initialize (one-time)
   └─> Create project from cookiecutter template
   └─> Generate SSL certificates
   └─> Create symlinks

2. nrp check (before first run)
   └─> Check infrastructure (docker, node, npm)
   └─> Create/verify virtualenv
   └─> Build requirements (uv pip compile)
   └─> Install Python packages (uv pip sync)
   └─> Install Invenio config
   └─> Start Docker containers
   └─> Build UI
   └─> Initialize database
   └─> Setup OpenSearch
   └─> Setup S3

3. nrp develop (development)
   └─> Start Python server
   └─> Start Webpack server
   └─> Start file watcher

4. nrp build (production)
   └─> Recreate virtualenv
   └─> Install all dependencies
   └─> Build UI
   └─> Prepare for production
```

---

## Detailed Commands Run by `nrp develop`

When you run `nrp develop`, the following exact commands are executed in sequence:

### Step 1: Check Docker Environment
```bash
# Check if docker/.env exists (symlink check)
# If missing, create:
ln -s variables docker/.env
```

### Step 2: Docker Health Check
```bash
docker ps
```

### Step 3: Docker Compose Version Check
```bash
docker compose version
```

### Step 4: Node Version Check
```bash
node --version
```

### Step 5: NPM Version Check
```bash
npm --version
```

### Step 6: ImageMagick Check
```bash
convert --version
```

### Step 7: Virtualenv Check
```bash
.venv/bin/python --version
.venv/bin/pip list
```

### Step 8: Requirements Check
```bash
# Checks if requirements.txt exists and is up to date
# If rebuild needed:
uv pip compile --prerelease allow pyproject.toml -o requirements.txt
```

### Step 9: Install Python Repository (if needed)
```bash
# In temporary project directory .nrp/oarepo-pdm:
uv pip compile --prerelease allow pyproject.toml -o requirements.txt

# Export requirements:
cat requirements.txt

# Resolve and install:
uv pip sync requirements-resolved-local.txt
uv pip install -e .
```

### Step 10: Install Invenio Configuration
```bash
# Create symlinks:
ln -sf /path/to/repo/invenio.cfg .venv/var/instance/invenio.cfg
ln -sf /path/to/repo/variables .venv/var/instance/variables
```

NOTE: It seems that these need to be copied, not symlinked.

### Step 11: Install Local Packages (if any with -e flag)
```bash
.venv/bin/pip install --config-settings editable_mode=compat -e /path/to/local/package
```

### Step 12: Start Docker Containers
```bash
docker compose up -d cache db mq search s3
```

### Step 13: UI Build (if needed)
```bash
# Collect assets:
INVENIO_INSTANCE_PATH=.venv/var/instance invenio oarepo assets collect .venv/var/instance/watch.list.json

# Create webpack config:
INVENIO_INSTANCE_PATH=.venv/var/instance invenio webpack clean create

# Install npm packages:
INVENIO_INSTANCE_PATH=.venv/var/instance invenio webpack install

# Build production UI:
INVENIO_INSTANCE_PATH=.venv/var/instance invenio webpack build --production

# Modify webpack config (disable clean):
# Replace "dry: false" with "dry: true" in .venv/var/instance/assets/build/webpack.config.js
```

NOTE: It needs to be `invenio webpack install --legacy-peer-deps`

### Step 14: Database Check/Initialization
```bash
# Check database status:
.venv/bin/invenio oarepo check /tmp/tempfile.json

# If not initialized:
.venv/bin/invenio db create

# If migration pending:
.venv/bin/invenio alembic upgrade heads
```

### Step 15: Copy Translations
```bash
# Get site-packages directory:
.venv/bin/python -c "import site; print(site.getsitepackages()[0])"

# Copy from oarepo:
cp .venv/lib/python3.13/site-packages/oarepo/collected_translations/** \
   .venv/lib/python3.13/site-packages/
```

### Step 16: Copy Assets to Webpack Build Directory
```bash
# Collect watched paths from .venv/var/instance/watch.list.json
# Copy files from source directories to:
#   - .venv/var/instance/static
#   - .venv/var/instance/assets
```

### Step 17: Start Python Server
```bash
cd /path/to/repository
FLASK_DEBUG=1 \
INVENIO_TEMPLATES_AUTO_RELOAD=1 \
.venv/bin/invenio run \
  --cert docker/development.crt \
  --key docker/development.key
```

### Step 18: Start Webpack Server
```bash
cd .venv/var/instance/assets
npm run start
```

### Step 19: Start File Watcher
```bash
# Uses watchdog library to watch paths from watch.list.json
# On file changes, copies to .venv/var/instance/static or .venv/var/instance/assets
```

### Step 20: Start Development Controller
```bash
# Interactive menu loop showing:
# - "server" option to restart Python server
# - "ui" option to restart Webpack server
# - "stop" option to stop all servers
```

