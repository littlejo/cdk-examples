from aws_cdk import (
    core,
    aws_ec2 as _ec2,
    aws_ecs as _ecs,
    aws_ecr as _ecr,
    aws_iam as _iam,
)

import sys
sys.path.insert(0,'..')
import base_platform as bp

class ECRStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, name_extension: str, stage:str, tags:[], vpc_name:str, region:str, ecs_conf:dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.base_platform = bp.BasePlatform(self, id, name_extension, stage, vpc_name)
        self.objects_list = []

        self.ec2_task_def = _ecs.Ec2TaskDefinition(
            self, 
            "rabbitmq",
            family=ecs_conf["task_name"],
            network_mode=_ecs.NetworkMode.AWS_VPC
        )

        self.container = self.ec2_task_def.add_container(
            "rabbitmq",
            cpu=256,
            memory_limit_mib=512,
            image=_ecs.ContainerImage.from_registry("littlejo/rabbitmq:3"),
            memory_reservation_mib=512,
            logging=_ecs.LogDriver.aws_logs(
                stream_prefix=name_extension+"-rabbitmq-container"
            ),
            environment={
                "RABBITMQ_ERLANG_COOKIE": "miammiam",
                "RABBITMQ_HOSTNAME": ecs_conf["dns_name"],
            },
        )

        self.container.add_port_mappings(
            _ecs.PortMapping(
                container_port=5672
            ),
            _ecs.PortMapping(
                container_port=4369
            ),
        )

        self.ec2_service = _ecs.Ec2Service(
            self, 
            "lz-rabbitmq-service",
            task_definition=self.ec2_task_def,
            cluster=self.base_platform.ecs_cluster,
            security_group=self.base_platform.services_sec_grp,
            desired_count=1,
            cloud_map_options=_ecs.CloudMapOptions(
                cloud_map_namespace=self.base_platform.sd_namespace,
                name=ecs_conf["dns_name"]
            ),
            service_name=ecs_conf["service_name"],
        )

        self.objects_list.append(self.ec2_service)
        self.objects_list.append(self.container)
        self.objects_list.append(self.ec2_task_def)
        self.tags_creation(tags)

    def tags_creation(self, tags):
        for o in self.objects_list:
            for tag in tags:
                core.Tag.add(o, tag.key, tag.value)
