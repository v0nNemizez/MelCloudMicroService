#!/bin/bash

imagename="melcloudmicroservice"
port="8000:8000"



echo "Starting Docker build"
docker build -t skogum/$imagename:0.0.2 -t skogum/$imagename:latest .

echo "Stopping running container"
docker stop $imagename

echo "Removing old container"
docker rm $imagename

echo "Starting container"
docker run -d -p 8000:8000 --name $imagename skogum/$imagename:latest

echo "Connecting to test network"
docker network connect microservice-test-network $imagename

echo "IP:"
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $imagename



