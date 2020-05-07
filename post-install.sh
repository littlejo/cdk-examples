#!/bin/bash

cp /etc/skel/.bashrc /root/
echo "export PATH=\$PATH:/usr/local/lib/node_modules/aws-cdk/bin/" >> /root/.bashrc
cd /root
bash
