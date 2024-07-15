# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Copy wordlist 
COPY wordlist.txt wordlist.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY enumerationtools.py .

ENV PORT 7000

# Expose port
EXPOSE 7000

# Command to run the application
CMD ["python", "enumerationtools.py"]
