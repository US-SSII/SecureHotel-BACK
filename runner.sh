#!/bin/bash

# Function to remove containers and images if they exist
clean_docker() {
    echo "Cleaning containers..."
    if docker ps -aq &>/dev/null; then
        docker rm -f $(docker ps -aq)
    fi

    echo "Cleaning images..."
    if docker images -aq &>/dev/null; then
        docker rmi -f $(docker images -aq)
    fi
}

# Call the function to clean Docker
clean_docker

# Build the server image
docker build -t server -f Dockerfile_server .
docker run -d -p 12345:12345 server

# Build the client image and run the container
docker build -t client -f Dockerfile_client .
winpty docker run -it --env HOST_IP=host.docker.internal --env PORT=12345 client

