FROM python:3.11-slim

WORKDIR /app

# Install SSH server and required packages
RUN apt-get update && apt-get install -y \
    openssh-server \
    && mkdir -p /var/run/sshd \
    && mkdir -p /root/.ssh \
    && chmod 700 /root/.ssh \
    && echo 'root:password' | chpasswd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p templates static

# Expose the ports for the app and SSH
EXPOSE 5000 22

# Create a startup script to run both sshd and gunicorn
RUN echo '#!/bin/bash\n\
/usr/sbin/sshd\n\
exec gunicorn --bind 0.0.0.0:5000 app:app' > /start.sh && \
    chmod +x /start.sh

# Command to run both services
CMD ["/start.sh"]
