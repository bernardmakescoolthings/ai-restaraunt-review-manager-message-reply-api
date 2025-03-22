#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Docker
install_docker() {
    echo "Installing Docker..."
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
        "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker $USER
    echo "Docker installed successfully!"
}

# Function to check if Docker is running
check_docker_running() {
    if ! sudo systemctl is-active --quiet docker; then
        echo "Starting Docker service..."
        sudo systemctl start docker
    fi
}

# Main setup process
echo "Starting setup process..."

# Install Docker if not present
if ! command_exists docker; then
    install_docker
fi

# Ensure Docker is running
check_docker_running

# Create application directory if it doesn't exist
APP_DIR="$HOME/restaurant-review-api"
if [ ! -d "$APP_DIR" ]; then
    echo "Creating application directory..."
    mkdir -p "$APP_DIR"
fi

# Copy application files to the directory
echo "Copying application files..."
cp -r ./* "$APP_DIR/"

# Navigate to application directory
cd "$APP_DIR"

# Build and run the Docker container
echo "Building and running the application..."
docker build -t restaurant-review-api .

# Stop and remove existing container if it exists
docker stop restaurant-review-api || true
docker rm restaurant-review-api || true

# Run the new container
docker run -d \
    --name restaurant-review-api \
    -p 8000:8000 \
    --env-file .env \
    restaurant-review-api

# Check if container is running
if docker ps | grep -q restaurant-review-api; then
    echo "Application is now running!"
    echo "You can access the API at http://localhost:8000"
    echo "To view logs, run: docker logs restaurant-review-api"
else
    echo "Failed to start the application. Check logs with: docker logs restaurant-review-api"
    exit 1
fi 