# Developer Guide: Publishing to Docker Hub

This guide explains how to build and publish the ASReview Reviewer Analytics Dashboard Docker image to Docker Hub so others can pull it directly without building it from source.

## Prerequisites
1. Create an account on [Docker Hub](https://hub.docker.com/).
2. Ensure you have Docker installed and running on your machine.

## 1. Login to Docker Hub
Open your terminal and authenticate your local Docker client:
```bash
docker login
```
Enter your Docker Hub username and password (or access token) when prompted.

## 2. Build and Tag the Image
Build the image and tag it with your Docker Hub username. Replace `<your-username>` with your actual Docker Hub username.
```bash
docker build -t <your-username>/asreview-dashboard:latest .
```

## 3. Push the Image
Upload the built image to the Docker Hub registry:
```bash
docker push <your-username>/asreview-dashboard:latest
```

## 4. (Optional) Provide Instructions for Users
Once published, users won't need to build the image from source. They can update the `docker-compose.yaml` file to use your published image instead of building it locally:
```yaml
services:
  dashboard:
    image: <your-username>/asreview-dashboard:latest
    # build: .  <-- This can be removed or commented out
```
