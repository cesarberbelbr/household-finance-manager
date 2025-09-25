# Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies needed for psycopg2
# RUN rm -rf /var/lib/apt/lists/* 
# RUN apt-get install -y build-essential libpq-dev 
# RUN rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .