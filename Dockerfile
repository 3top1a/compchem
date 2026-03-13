FROM debian:trixie-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    gcc \
    g++ \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-2.0-dev \
    libglib2.0-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    curl \
    git \
    imagemagick \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY invenio.cfg variables ./

# Install Python dependencies
RUN uv sync

# Copy the rest of the application
COPY . .

# Create instance directory and copy config
RUN mkdir -p .venv/var/instance && \
    cp invenio.cfg .venv/var/instance/invenio.cfg && \
    cp variables .venv/var/instance/variables

# Add .venv/bin to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose ports
EXPOSE 5000

CMD ["bash"]

