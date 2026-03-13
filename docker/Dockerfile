# Dockerfile for compchem repository
# Uses shell.nix for environment setup

FROM nixos/nix:2.24.0 AS builder

WORKDIR /app

# Copy project files
COPY . .

# Build the development environment using shell.nix
# This will install all dependencies: uv, nodejs, docker, imagemagick, etc.
RUN nix-shell --run "\
  uv sync --frozen && \
  uv pip install -e . && \
  invenio webpack install --legacy-peer-deps"

# Set environment variables
ENV FLASK_DEBUG=1
ENV INVENIO_TEMPLATES_AUTO_RELOAD=1
ENV INVENIO_INSTANCE_PATH=/app/.venv/var/instance
ENV UV_SYSTEM_PYTHON=0

# Copy configuration files
RUN mkdir -p .venv/var/instance
COPY invenio.cfg .venv/var/instance/invenio.cfg
COPY variables .venv/var/instance/variables

# Expose the application port
EXPOSE 5000

# Default command: start development server
CMD ["invenio", "run"]
