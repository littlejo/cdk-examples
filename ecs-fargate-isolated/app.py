#!/usr/bin/env python3

from aws_cdk import core

import json
import os

from environment.environment_stack import EnvironmentStack
from ecr.task_ecr_stack import ECRStack

# Read global configuration file 
with open('environment_conf.json') as config_file:
    global_conf = json.load(config_file)

app = core.App()
stage = app.node.try_get_context("stage")

if stage is None :
    stage = "dev"

print("# Deploy stage [{}]".format(stage))

common_tags = []
common_tags.append( core.CfnTag( key="Project", value=global_conf["global"]["project"]))
common_tags.append( core.CfnTag( key="Stage", value=stage))

env = core.Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
    region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"])
)

EnvironmentStack(app, f"env-{stage}", tags=common_tags, name_extension=global_conf["global"]["extension"]+stage, stage=stage, conf=global_conf, env=env )
ECRStack(app, f"ecr-{stage}", tags=common_tags, name_extension=global_conf["global"]["extension"]+stage, stage=stage , vpc_name=global_conf[stage]["vpc_name"] , region=os.environ["CDK_DEFAULT_REGION"], env=env, ecs_conf=global_conf[stage]["ecs"]["nginx-1"])
ECRStack(app, f"ecr-2-{stage}", tags=common_tags, name_extension=global_conf["global"]["extension"]+stage, stage=stage , vpc_name=global_conf[stage]["vpc_name"] , region=os.environ["CDK_DEFAULT_REGION"], env=env, ecs_conf=global_conf[stage]["ecs"]["nginx-2"])

app.synth()
