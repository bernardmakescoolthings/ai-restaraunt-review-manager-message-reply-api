#!/bin/bash

# Build the Docker image
docker build -t restaurant-review-api .

# Run the container
docker run -d \
  --name restaurant-review-api \
  -p 8000:8000 \
  --env-file .env \
  restaurant-review-api 