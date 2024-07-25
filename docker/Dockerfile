# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code to the container
COPY bot.py .

# Copy the environment file to the container
COPY .env .

# Set the command to run your bot when the container starts
CMD ["python", "bot.py"]