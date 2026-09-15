from aws_cdk import(
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    Fn,
    aws_ec2 as ec2,
    aws_rds as rds,
)
from constructs import Construct


class DatabaseStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id:str,
        **kwargs,
    ) -> None:
        super().__init__(scope,construct_id,**kwargs)
        
        #To explicitly specify the Availability Zone
        #(Because it was difficult to dynamically retrieve the Availability Zone from the instance.)
        AZs = ["ap-northeast-1a","ap-northeast-1c","ap-northeast-1d"]
        writer_az = AZs[0]
        reader_az = AZs[1]
        
        
        vpc = ec2.Vpc(
            self,"Vpc",
            
            #Set max_azs to 2 or more for multi-AZ.
            max_azs = 2,
            
            #To avoid unnecessary costs
            nat_gateways = 0,
            
            #To deny public access
            subnet_configuration = [
                ec2.SubnetConfiguration(
                    name = "Isolated",
                    subnet_type = ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask = 24,
                ),
            ],
        )
        
        
        db = rds.DatabaseCluster(
            self,"Postgres",
            
            #To specify the database engine
            engine = rds.DatabaseClusterEngine.aurora_postgres(
                version = rds.AuroraPostgresEngineVersion.VER_15_8,
            ),
            
            #To specify the instance class and Availability Zone.
            writer = rds.ClusterInstance.serverless_v2("writer",availability_zone = writer_az),
            readers=[
                rds.ClusterInstance.serverless_v2("reader1",availability_zone = reader_az),
            ],
            
            
            #To specify the Minimum ACU and Maximum ACU
            #It was not possible to set the maximum ACU to 8.0 under the free plan. 
            #I am changing the maximum ACU to 4.0.
            serverless_v2_max_capacity = 4.0,
            serverless_v2_min_capacity = 0.5,
            
            #To deploy to a private subnet
            vpc = vpc,
            vpc_subnets = ec2.SubnetSelection(
                subnet_type = ec2.SubnetType.PRIVATE_ISOLATED
            ),
            
            #To protect administrator credentials
            credentials = rds.Credentials.from_generated_secret("dbadmin"),
            
            #To protect data
            storage_encrypted = True,
            delete_automated_backups = True,
            
            
            
        )
        
        #Include it as a field for verification during integration testing.
        self.credentials = db.secret
        
        
        #To output the Cluster Endpoint string
        CfnOutput(self,"DbClusterEndpoint",value = db.cluster_endpoint.hostname)
        
        #To output the Reader Endpoint string
        CfnOutput(self,"DbClusterReaderEndpoint",value = db.cluster_read_endpoint.hostname)
        
        
        #To verify that the Writer and Reader are deployed in different Availability Zones.
        CfnOutput(self,"DbClusterWriterAZ",value=writer_az)
        CfnOutput(self,"DbClusterReaderAZ",value=reader_az)

