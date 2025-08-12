# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy pyproject.toml and poetry.lock first to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# Install project dependencies
RUN poetry install --no-root

# Copy the rest of the application code
COPY . /app/

# Expose port 8000 for the Django application
EXPOSE 8000

# Command to run the Django development server (this will be overridden by docker-compose for dev)
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
