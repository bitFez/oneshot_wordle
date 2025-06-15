# Start with ARG that can be used by the first FROM instruction.
ARG PYTHON_VERSION=3.12-slim-bookworm # <--- CHANGE THIS LINE

# Define the base Python image. This will be aliased as 'python' for multi-stage builds.
FROM python:${PYTHON_VERSION} as python

# ---

# Python build stage
# This stage is responsible for installing build tools and creating Python wheels.
FROM python as python-build-stage

# Define the build environment, defaulting to 'production'.
ARG BUILD_ENVIRONMENT=production

# Install apt packages required for building Python packages (e.g., build-essential, libpq-dev).
# Also install 'curl' to download 'uv'.
# The `&& rm -rf /var/lib/apt/lists/*` cleans up apt cache immediately to reduce layer size.
RUN apt-get update -o Acquire::AllowInsecureRepositories=true -o Acquire::AllowDowngradeToInsecureRepositories=true && \
    apt-get install --no-install-recommends -y \
        debian-archive-keyring \
        dirmngr \
        build-essential \
        libpq-dev \
        curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/ && \
    apt-get purge -y --auto-remove curl && \
    rm -rf /var/lib/apt/lists/*

# IMPORTANT: Copy the ENTIRE 'requirements' directory.
# This ensures that if production.txt includes other files like base.txt, they are all present.
COPY ./requirements/ /usr/src/app/requirements/

# Create Python Dependency and Sub-Dependency Wheels using standard 'pip wheel'.
# 'uv' does not have a 'wheel' subcommand. We use standard 'pip' for this.
# Wheels are stored in /usr/src/app/wheels, which will be copied to the run stage.
RUN pip wheel --wheel-dir /usr/src/app/wheels \
    -r /usr/src/app/requirements/${BUILD_ENVIRONMENT}.txt
# ---

# Python 'run' stage
# This stage builds the final, lean image for running your application in production.
# It also uses 'python' as its base image.
FROM python as python-run-stage

# Define arguments for the build environment and application home directory.
ARG BUILD_ENVIRONMENT=production
ARG APP_HOME=/app

# Set environment variables for Python to improve performance and logging in Docker.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

# Set the working directory for the application inside the container.
WORKDIR ${APP_HOME}

# Create a dedicated system user and group for the application ('django') for security best practices.
RUN addgroup --system django \
    && adduser --system --ingroup django django

# Install required system dependencies for runtime (e.g., libpq-dev for psycopg2, gettext for translations).
# 'uv' is NOT installed here as it's not needed in the final runtime image, keeping it smaller.
# The apt cache is purged immediately after installation.
RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq-dev \
    gettext \
    # Add any other runtime-specific apt packages here (e.g., nginx if serving static files)
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# Copy the pre-built Python dependency wheels from the 'python-build-stage' into the current stage.
COPY --from=python-build-stage /usr/src/app/wheels /wheels/

# Install Python dependencies from the copied wheels using standard 'pip install'.
# `--no-cache-dir` reduces image size by not storing pip's cache.
# `--no-index --find-links=/wheels/` tells pip to only look for packages in the /wheels/ directory.
# The wheels directory is then removed as it's no longer needed.
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

# Copy entrypoint and start scripts into the container.
# `sed -i 's/\r$//g'` removes Windows carriage returns if the files were created on Windows.
# `chmod +x` makes the scripts executable.
# `--chown=django:django` sets the ownership to the 'django' user for security.
COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# Copy your application code from the current directory on the host to the WORKDIR in the container.
# `--chown=django:django` sets the ownership of the copied files to the 'django' user.
COPY --chown=django:django . ${APP_HOME}

# Ensure the entire application directory in the container is owned by the 'django' user.
RUN chown -R django:django ${APP_HOME} # Changed to -R for recursive ownership

# Switch to the non-root 'django' user for running the application.
# This is a security best practice.
USER django

# Define the default command to run when the container starts.
# This points to your entrypoint script.
ENTRYPOINT ["/entrypoint"]

# CMD specifies the default command that will be executed if no command is provided when the container starts.
# Often used with ENTRYPOINT, where ENTRYPOINT defines the executable and CMD provides default arguments.
# For example, your /entrypoint might exec gunicorn, and CMD could specify the app module.
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] # Example, replace with your actual CMD