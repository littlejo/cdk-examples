#!/bin/bash

repo_name=nginx

aws ecr create-repository --repository-name $repo_name > /dev/null
ecr_repo=$(aws ecr describe-repositories --repository-names $repo_name | jq -M '.repositories[0].repositoryUri' | sed 's/"//g')
docker pull nginx
docker tag nginx:latest $ecr_repo
aws ecr get-login-password --region eu-west-3 | docker login --username AWS --password-stdin $ecr_repo
docker push $ecr_repo:latest
