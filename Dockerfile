FROM ubuntu:20.04

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y curl python3-pip vim bash-completion git jq nodejs npm

RUN pip3 install awscli
RUN npm install -g --no-bin-links aws-cdk

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ADD post-install.sh /var/tmp
RUN chmod a+x /var/tmp/post-install.sh

#./launch-instance.sh AKIAVZZ64MGKZVQBLX5D wDzLxH4woSoHGOP0faqGirnjwxOU7/oYrR4xRls5
