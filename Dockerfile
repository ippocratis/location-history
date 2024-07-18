# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container to /app (root directory in this context)
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the entrypoint script
ENTRYPOINT ["sh", "entrypoint.sh"]
