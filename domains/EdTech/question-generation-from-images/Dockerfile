# Use a base image with Python 3.10
FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip \
    && pip install -e .

# Expose the desired port (change as needed)
EXPOSE 8014

# Command to run the application
CMD ["qfi-start"]