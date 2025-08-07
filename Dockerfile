# Ubuntu 20.04 build environment for GitLab MCP server
FROM ubuntu:20.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.8 and build dependencies
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3.8-dev \
    python3.8-venv \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.8 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

WORKDIR /app

# Copy project files
COPY requirements.txt .
COPY mcp_server.py .

# Install Python dependencies compatible with Python 3.8
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install requests==2.28.2 urllib3==1.26.18 certifi charset-normalizer idna
RUN python3 -m pip install pyinstaller

# Create the binary
RUN python3 -m PyInstaller --onefile --name gitlab-mcp-server \
    --hidden-import=requests \
    --hidden-import=urllib3 \
    --hidden-import=urllib3.util \
    --hidden-import=urllib3.util.retry \
    --hidden-import=urllib3.contrib \
    --hidden-import=urllib3.contrib.pyopenssl \
    mcp_server.py

# The binary will be in /app/dist/gitlab-mcp-server
CMD ["/bin/bash"]
