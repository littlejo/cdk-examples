from aws_cdk import (
    core,
    aws_ec2 as _ec2,
    aws_ecs as _ecs,
    aws_servicediscovery as _servicediscovery
)

# Creating a construct that will populate the required objects created in the platform repo such as vpc, ecs cluster, and service discovery namespace
class BasePlatform(core.Construct):
    def __init__(self, scope: core.Construct, id: str, name_extension: str,  stage:str, vpc_name:str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # The base platform stack is where the VPC was created, so all we need is the name to do a lookup and import it into this stack for use
        self.vpc = _ec2.Vpc.from_lookup(
            self, name_extension+"VPC",
            vpc_name = vpc_name
        )

        self.sd_namespace = _servicediscovery.PrivateDnsNamespace.from_private_dns_namespace_attributes(
            self, name_extension+"SDNamespace",
            namespace_name=core.Fn.import_value(f'ns-name-{stage}'),
            namespace_arn=core.Fn.import_value(f'ns-arn-{stage}'),
            namespace_id=core.Fn.import_value(f'ns-id-{stage}')
        )

        self.ecs_cluster = _ecs.Cluster.from_cluster_attributes(
            self, name_extension+"ECSCluster",
            cluster_name=core.Fn.import_value(f'ecs-name-{stage}'),
            security_groups=[],
            vpc=self.vpc,
            default_cloud_map_namespace=self.sd_namespace
        )

        self.services_sec_grp = _ec2.SecurityGroup.from_security_group_id(
            self, name_extension+"ServicesSecGrp",
            security_group_id=core.Fn.import_value(f'ecs-sg-id-{stage}')
        )

