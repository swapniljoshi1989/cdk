from aws_cdk import Stack,CfnOutput
from constructs import Construct

from aws_cdk import aws_ec2 as ec2,aws_rds as rds


class NetworkStack(Stack):
    def __init__(self,scope:Construct,construct_id:str,**kwargs):
        super().__init__(scope,construct_id,**kwargs)
        
        self.vpc=ec2.Vpc(self,"VPC",
            availability_zones=[
                "ap-northeast-3a",
                "ap-northeast-3b"
            ],
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            create_internet_gateway=False,
            nat_gateway_provider=None,
            nat_gateways=0,
            nat_gateway_subnets=None,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PrivateSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ],
        )
        
        self.subnet_group = rds.SubnetGroup(self,"PrivateSubnetGroup",
            description="subnet group for rds",
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            )
        )
