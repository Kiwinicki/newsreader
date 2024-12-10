FROM python:3.12.7-alpine3.20

ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apk add --update --no-cache postgresql-client gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev curl

# Create a non-root user
RUN adduser -D user

# Create and set ownership of necessary directories
WORKDIR /app
RUN mkdir -p /home/user/.local /home/user/.cache \
    && chown -R user:user /app /home/user/.local /home/user/.cache

# Switch to non-root user
USER user

# Set environment variables for Poetry
ENV POETRY_HOME="/home/user/.local"
ENV PATH="/home/user/.local/bin:$PATH"
ENV POETRY_CACHE_DIR="/home/user/.cache/pypoetry"

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true

# Copy Poetry configuration files
COPY --chown=user:user pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Copy project files
COPY --chown=user:user newsreader ./newsreader

# Copy the SQL initialization script
COPY --chown=user:user init.sql /docker-entrypoint-initdb.d/init.sql

# Run the app using Poetry
CMD ["poetry", "run", "uvicorn", "newsreader.main:app", "--host", "0.0.0.0", "--port", "8000"]