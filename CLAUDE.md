# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development

- `./nrp check` - Verify prerequisites and repository readiness
- `./nrp check --fix` - Attempt to fix detected issues
- `./nrp develop --extra-library <path>` - Start development server with optional extra library
- `./nrp build` - Build repository for production
- `./nrp run` - Run the repository in production mode
- `./nrp test` - Run integration API and UI tests
- `./nrp upgrade` - Upgrade dependencies and rebuild

### Model Management

- `./nrp model create <model-name>` - Create a new model
- `./nrp model compile <model-name>` - Compile model to Python code

### UI Management

- `./nrp ui model create --model <model-name> [ui-name]` - Create UI pages for a model
- `./nrp ui page create <page-name> [page-endpoint]` - Create UI pages for custom endpoints
- `./nrp ui page create <page-name> <page-endpoint> --react` - Create UI with React endpoint

### Docker

The project uses Docker Compose with services: `db`, `cache`, `mq`, `search`, `s3`.

## Architecture

This is an InvenioRDM-based computational chemistry repository with:

### Core Structure
- **experiments/** - Main record type for computational chemistry experiments with files, workflows, and requests
- **shared/** - Custom services (e.g., file processors), workflows, and Alembic migrations
- **models/** - YAML schema definitions for records, files, definitions, and custom fields
- **ui/** - React/SEMANTIC-UI frontend with JinjaX templates
- **oarepo.yaml/** - Model builder configuration

### Key Components
- **Records**: Draft/published workflow with versioning via SQLAlchemy-Continuum
- **Files**: S3-backed file storage with custom processors (e.g., TPR parameter extraction)
- **Workflows**: Custom workflow system with permissions in `shared/workflows/`
- **Requests**: Community-based review requests with custom resolvers
- **Vocabularies**: NR-METADATA and NR-VOCABULARIES integration

### Python Package Structure
- Custom models compiled to `experiments/` with records, services, resources, views
- Services follow pattern: `services/records/published/` for published records
- File services in `services/files/published/`
- Permissions configured via generators in `services/records/permissions.py`

### Frontend
- Webpack theme bundles in `ui/*/webpack.py`
- React components using JSON Forms for dynamic forms
- Semantic UI integration

## Important Notes
- Python 3.12 required (requires `requires-python = "~=3.12.0"`)
- Node 21 required for frontend
- Uses `uv` for Python dependency management
- Development requires fixing webpack legacy-peer-deps issue (see `how-to-start.md`)
- Uses CESNET's PyPI registry for packages
