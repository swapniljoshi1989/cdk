import aws_cdk as cdk
import pytest
import os

from aws_cdk import App
from aws_cdk.assertions import Template,Match
from first_task.database_stack import DatabaseStack
from first_task.network_stack import NetworkStack
@pytest.fixture
def template():
    app = App()
    env = cdk.Environment(
        account = "338071012882",
        region = "ap-northeast-3"
    )
    network = NetworkStack(app,"TestNetworkStack")
    dababase = DatabaseStack(app,"TestDatabaseStack",network.vpc,network.subnet_group)
    return Template.from_stack(dababase)

@pytest.mark.parametrize("parameter_key,expected_value",[
    #Check if the database engine is Aurora postgreSQL
    ("Engine","aurora-postgresql"),
    #Check if the engine version is 15.8
    ("EngineVersion","15.8"),
    #Check if Max ACU is 8.0, Min ACU is 0.5
    ("ServerlessV2ScalingConfiguration",{
        "MaxCapacity" : 8.0,
        "MinCapacity" : 0.5
    }),
    #Check if RDS uses AWS Secrets Manager
    ("ManageMasterUserPassword",True)
])

def test_configurations(template,parameter_key,expected_value):
    template.has_resource_properties("AWS::RDS::DBCluster",
        Match.object_like({ parameter_key : expected_value })
    )

#Check if the DB instances are created only 2
def test_db_instances_count(template):
    template.resource_count_is("AWS::RDS::DBInstance",2)

#Check if the both of instances are located in different A-Z
def test_instances_in_different_availability_zones(template):
    template.has_resource_properties("AWS::RDS::DBInstance",
        Match.object_like({"AvailabilityZone":"ap-northeast-3a"})
    )
    template.has_resource_properties("AWS::RDS::DBInstance",
        Match.object_like({"AvailabilityZone":"ap-northeast-3b"})
    )

@pytest.mark.parametrize("common_property,common_parameter",[
    #Check if both of reader and writer are private
    ("PubliclyAccessible",False),
    #Check if the both instance class of instances are "serverless"
    ("DBInstanceClass","db.serverless")
])

def test_publicly_accessible(template,common_property,common_parameter):
    template.resource_properties_count_is("AWS::RDS::DBInstance",
        Match.object_like({common_property:common_parameter}),
        2
    )
