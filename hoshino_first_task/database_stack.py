from aws_cdk import Stack,CfnOutput
from constructs import Construct

from aws_cdk import aws_rds as rds,aws_ec2 as ec2

class DatabaseStack(Stack):
    def __init__(self, scope:Construct,construct_id:str,vpc:ec2.IVpc,db_subnet_group_ref:rds.IDBSubnetGroupRef,**kwargs):
        super().__init__(scope,construct_id,**kwargs)
        
        self.aurora_dbs = rds.DatabaseCluster(self,"AuroraDatabase",
            #Use Aurora PostgreSQL version:15.8 as this database engine
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_15_8
            ),
            #Use default VPC of the region
            vpc=vpc,
            #Set private subnet group
            subnet_group=db_subnet_group_ref,
            #Set min ans max of ACU
            serverless_v2_max_capacity=8.0,
            serverless_v2_min_capacity=0.5,
            #Enable to use AWS Secrets Manager
            manage_master_user_password=True,
            
            readers=[
                #Set serverless V2 as instance type
                rds.ClusterInstance.serverless_v2("reader",
                    #Set availability zone (intentionally to locate in different A-Z)
                    availability_zone="ap-northeast-3a",
                    #Set not to be accessed publicly
                    publicly_accessible=False
                )
            ],
            #
            writer=(
                #Set serverless V2 as instance type
                rds.ClusterInstance.serverless_v2("writer",
                    #Set availability zone (intentionally to locate in different A-Z)
                    availability_zone="ap-northeast-3b",
                    #Set not to be accessed publicly
                    publicly_accessible=False
                )
            )
        )
        
        CfnOutput(self,"Cluster Endpoint",value=self.aurora_dbs.cluster_endpoint.hostname)
        CfnOutput(self,"Reader Endpoint",value=self.aurora_dbs.cluster_read_endpoint.hostname)
