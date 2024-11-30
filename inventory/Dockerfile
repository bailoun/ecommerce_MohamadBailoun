# Inside customers/Dockerfile
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt from the build context (root directory)
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service's code into the container
COPY . /app/

# Expose the application port (adjust if necessary)
EXPOSE 5002

# Set the default command to run the Flask app
CMD ["python", "app.py"]
