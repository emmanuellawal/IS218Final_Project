# Dockerfile

# Base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir flask sqlalchemy openai

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "personalized_study_assistant.py"]
