FROM python:3.10-slim

# Use /app as the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and entrypoint
COPY main.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Expose HTTP port
EXPOSE 8080

# Run entrypoint to inject Vault secrets then start app
ENTRYPOINT ["./entrypoint.sh"]
