import pytest
import aws_cdk as cdk
from aws_cdk.assertions import Template,Match
from first_task.database_stack import DatabaseStack

@pytest.fixture
def template():
    app = cdk.App()
    stack = DatabaseStack(app,"DatabaseTest")
    return Template.from_stack(stack)

@pytest.mark.parametrize("resource,count",[
    ("AWS::EC2::VPC",1),
    ("AWS::EC2::Subnet",2),
    ("AWS::EC2::NatGateway",0),
    ("AWS::RDS::DBInstance",2),
])

#Checking the number of created resources
def test_create_resource_count(template,resource,count):
    template.resource_count_is(resource,count)
    
    
#Confirming Public Access Denial
def test_not_public_access(template):
    template.has_resource_properties("AWS::RDS::DBInstance",{
        "PubliclyAccessible":False,
    })


#Checking database configuration settings
def test_rds_cluster_instance_config(template):
    template.has_resource_properties("AWS::RDS::DBInstance",{
        "DBInstanceClass":"db.serverless",
        "Engine":"aurora-postgresql",
    })
    
    template.has_resource_properties("AWS::RDS::DBCluster",{
        "ServerlessV2ScalingConfiguration":{
            "MaxCapacity":4.0,
            "MinCapacity":0.5,
        },
        
        "DeleteAutomatedBackups":True,
        "StorageEncrypted":True,
    })
    
    




