# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Upgrade pip and install the required packages
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose port 7500 for the FastAPI app
EXPOSE 7500

# Run the FastAPI server using uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7500"]
