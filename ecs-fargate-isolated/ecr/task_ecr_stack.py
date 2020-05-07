from aws_cdk import (
    core,
    aws_ec2 as _ec2,
    aws_ecs as _ecs,
    aws_ecr as _ecr,
    aws_iam as _iam,
    aws_servicediscovery as _servicediscovery
)

import sys
sys.path.insert(0,'..')
import base_platform as bp

class ECRStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, name_extension: str, stage:str, tags:[], vpc_name:str, region:str, ecs_conf:dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.base_platform = bp.BasePlatform(self, id, name_extension, stage, vpc_name)
        self.objects_list = []

        self.ecr = _ecr.Repository.from_repository_name(self, "nginx-ecr", repository_name="nginx")

        self.fargate_task_def = _ecs.FargateTaskDefinition(
            self, 
            "lz-nginx-ecr-td",
            family=ecs_conf["task_name"],
            cpu=256,
            memory_limit_mib=512,
        )

        self.container = self.fargate_task_def.add_container(
            "lz-nginx-ecr-container",
            image=_ecs.ContainerImage.from_ecr_repository(self.ecr, "latest"),
            memory_reservation_mib=512,
            logging=_ecs.LogDriver.aws_logs(
                stream_prefix=name_extension+"-nginx-container"
            ),
            environment={
                "REGION": region
            },
        )

        self.container.add_port_mappings(
            _ecs.PortMapping(
                container_port=80
            )
        )

        self.fargate_service = _ecs.FargateService(
            self, 
            "lz-nginx-ecr-service",
            task_definition=self.fargate_task_def,
            cluster=self.base_platform.ecs_cluster,
            security_group=self.base_platform.services_sec_grp,
            desired_count=1,
            cloud_map_options=_ecs.CloudMapOptions(
                cloud_map_namespace=self.base_platform.sd_namespace,
                name=ecs_conf["dns_name"]
            ),
            service_name=ecs_conf["service_name"],
        )

        self.objects_list.append(self.ecr)
        self.objects_list.append(self.fargate_service)
        self.objects_list.append(self.container)
        self.objects_list.append(self.fargate_task_def)
        self.tags_creation(tags)

    def tags_creation(self, tags):
        for o in self.objects_list:
            for tag in tags:
                core.Tag.add(o, tag.key, tag.value)
