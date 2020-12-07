# Dependencies

* you need to create nginx ecr and push from nginx docker hub
   * More info: install-nginx-ecr.sh

# What's it done

## env-dev stack

* create a vpc
* create 3 isolated subnets on each az (if there are 3 az on the region)
* create an ecs cluster

## ecr-dev stack

* create a task definition with nginx ecr
* create an ecs service using the task definition

## ecr-2-dev stack

* same as ecr-dev stack

# Deployment

make deploy-all


