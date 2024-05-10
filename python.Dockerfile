# Use an official Python runtime as a parent image
FROM python:3.12-slim-bullseye AS base

WORKDIR /app

# Create a non-root user
RUN addgroup --system --gid 10001 app && \
    adduser --system --ingroup app --uid 10001 app && \
    chown -R app:app /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PATH=/app/.venv/bin:${PATH}

# Install system dependencies
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Base build stage, install poetry
FROM base AS base_build

WORKDIR /app

RUN apt-get update -y &&  \
    apt-get upgrade -y &&  \
    apt-get -y install --no-install-recommends \
    build-essential \
    cmake \
    libssl-dev \
    libffi-dev \
    curl \
    git \
    openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p ~/.ssh && \
    ssh-keyscan -H github.com >> ~/.ssh/known_hosts

# Install Poetry
ARG POETRY_HOME=/opt/poetry
ARG POETRY_CACHE=${POETRY_HOME}/cache
ARG POETRY_CONFIG=${POETRY_HOME}/config
# Set the environment variables in Docker
ENV POETRY_HOME=$POETRY_HOME
ENV XDG_CACHE_HOME=$POETRY_CACHE
ENV XDG_CONFIG_HOME=$POETRY_CONFIG
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN mkdir -p $XDG_CACHE_HOME && chown -R app:app $XDG_CACHE_HOME
RUN mkdir -p $XDG_CONFIG_HOME && chown -R app:app $XDG_CONFIG_HOME
RUN pip install --no-cache-dir --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 -
RUN poetry config virtualenvs.create true && \
    poetry config virtualenvs.in-project true

# Build stage, install python dependencies
FROM base_build AS build

WORKDIR /app

# Copy pyproject.toml and, if present, the poetry.lock file
COPY --chown=app:app pyproject.toml  poetry.lock* ./

# Allow installing development and testing dependencies to develop or run tests
ARG ENVIRONMENT=production

# Install dependencies without virtualenv since we are inside a container
RUN --mount=type=ssh poetry lock --no-update && \
    if [ "$ENVIRONMENT" = "development" ] ; then \
    poetry install; \
    elif [ "$ENVIRONMENT" = "testing" ] ; then \
    poetry install --no-root --with test; \
    else \
    poetry install --no-root --only main; \
    fi


FROM base AS runner

WORKDIR /app

# Set the user to the non-root user
USER app

# Copy the virtualenv from the build stage
COPY --chown=app:app --from=build /app/.venv /app/.venv

# Copy the rest of the application files to the working directory
COPY --chown=app:app . .

# Set Python Path to the application
ENV PYTHONPATH=/app

# Expose port
EXPOSE ${APP_PORT}

# Run guinicorn
ENTRYPOINT ["/app/.venv/bin/gunicorn", "--preload"]