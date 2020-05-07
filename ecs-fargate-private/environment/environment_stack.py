from aws_cdk import (
    core,
    aws_ec2 as _ec2,
    aws_ecs as _ecs,
    aws_ecr as _ecr,
)

class EnvironmentStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, name_extension: str, stage:str, tags:[], conf: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.extension = name_extension
        self.objects_list = []
        self.vpc_creation(name_extension, conf, stage)

        # Namespace details as CFN output
        self.vpc_outputs = {
            'ID': self.vpc.vpc_id
        }
        self.cluster_creation(name_extension, conf, stage)

        self.tags_creation(tags)
        core.CfnOutput(self, f"output-vpc-{stage}", value=self.vpc_outputs['ID'], export_name=f"vpc-main-{stage}")

        core.CfnOutput(self, f"output-ns-arn-{stage}", value=self.namespace_outputs['ARN'], export_name=f"ns-arn-{stage}")
        core.CfnOutput(self, f"output-ns-name-{stage}", value=self.namespace_outputs['NAME'], export_name=f"ns-name-{stage}")
        core.CfnOutput(self, f"output-ns-id-{stage}", value=self.namespace_outputs['ID'], export_name=f"ns-id-{stage}")

        core.CfnOutput(self, f"output-ecs-name-{stage}", value=self.cluster_outputs['NAME'], export_name=f"ecs-name-{stage}")
        core.CfnOutput(self, f"output-ecs-arn-{stage}", value=self.cluster_outputs['ARN'], export_name=f"ecs-arn-{stage}")
        core.CfnOutput(self, f"output-ecs-sg-{stage}", value=self.cluster_outputs['SECGRPS'], export_name=f"ecs-sg-{stage}")

        core.CfnOutput(self, f"output-ecs-sg-id-{stage}", value=self.services_sg.security_group_id, export_name=f"ecs-sg-id-{stage}")


    def vpc_creation(self, name_extension, conf, stage):
        resource_name = name_extension+"-vpc.main"

        self.vpc = _ec2.Vpc(self, 
                            resource_name,
                            cidr=conf[stage]["vpc_cidr"],
                            max_azs=conf[stage]["vpc_az"],
                            nat_gateway_provider=_ec2.NatProvider.gateway(),
                            nat_gateways=conf[stage]["nat_gateways_num"],
                            subnet_configuration=[
                                _ec2.SubnetConfiguration(
                                subnet_type=_ec2.SubnetType.PUBLIC,
                                name="Public", 
                                cidr_mask=conf[stage]["subnet_cidr_mask"]
                                ),
                                _ec2.SubnetConfiguration(
                                subnet_type=_ec2.SubnetType.PRIVATE,
                                name="Private", 
                                cidr_mask=conf[stage]["subnet_cidr_mask"]
                                ),
                            ],
                           )

        endpoints_list = [
               ("logs", _ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS),
               ("ecr", _ec2.InterfaceVpcEndpointAwsService.ECR),
               ("ecr_dk", _ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER),
        ]
        for ep_str, svc in endpoints_list:
            ep = _ec2.InterfaceVpcEndpoint(self, ep_str, vpc=self.vpc, service=svc, subnets={"subnet_type": _ec2.SubnetType.PRIVATE})
            self.objects_list.append(ep)

        self.s3_ep = _ec2.GatewayVpcEndpoint(self, "s3", vpc=self.vpc, service=_ec2.GatewayVpcEndpointAwsService.S3, subnets=[_ec2.SubnetSelection(subnet_type=_ec2.SubnetType.PRIVATE)])
        self.objects_list.append(self.s3_ep)

        self.objects_list.append(self.vpc)
        core.Tag.add(self.vpc, "Name", conf[stage]["vpc_name"])

    def cluster_creation(self, name_extension, conf, stage):
        # Creating ECS Cluster in the VPC created above
        conf_global = conf["global"]["project"]
        self.ecs_cluster = _ecs.Cluster(
            self, name_extension+"-ecs-cluster",
            cluster_name=f"{conf_global}_{stage}",
            vpc=self.vpc
        )

        # Adding service discovery namespace to cluster
        self.ecs_cluster.add_default_cloud_map_namespace(
            name=name_extension,
        )

        # Namespace details as CFN output
        self.namespace_outputs = {
            'ARN': self.ecs_cluster.default_cloud_map_namespace.private_dns_namespace_arn,
            'NAME': self.ecs_cluster.default_cloud_map_namespace.private_dns_namespace_name,
            'ID': self.ecs_cluster.default_cloud_map_namespace.private_dns_namespace_id,
        }
        
        # Cluster Attributes
        self.cluster_outputs = {
            'NAME': self.ecs_cluster.cluster_name,
            'ARN': self.ecs_cluster.cluster_arn,
            'SECGRPS': str(self.ecs_cluster.connections.security_groups)
        }

        self.services_sg = _ec2.SecurityGroup(
            self, name_extension+"-ecs-cluster-services-sg",
            allow_all_outbound=True,
            description="Security group ECS {} services".format(name_extension),
            vpc=self.vpc
        )

        self.services_sg.add_ingress_rule(_ec2.Peer.ipv4("0.0.0.0/0"), _ec2.Port.tcp(80), "allow http access from anywhere")

        self.objects_list.append(self.ecs_cluster)
        self.objects_list.append(self.services_sg)

    def tags_creation(self, tags):
        for o in self.objects_list:
            for tag in tags:
                core.Tag.add(o, tag.key, tag.value)
