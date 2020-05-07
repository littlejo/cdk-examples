#!/bin/bash

image=littlejo/cdk-examples
aws_region=us-east-1


docker run -it -v $PWD:/root -e AWS_ACCESS_KEY_ID=$1 \
                                            -e AWS_SECRET_ACCESS_KEY=$2 \
                                            -e AWS_DEFAULT_REGION=$aws_region \
                                            --rm $image /var/tmp/post-install.sh
