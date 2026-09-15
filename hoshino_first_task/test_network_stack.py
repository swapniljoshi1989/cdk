import aws_cdk as cdk
import pytest

from aws_cdk import App
from aws_cdk.assertions import Template,Match
from first_task.network_stack import NetworkStack

@pytest.fixture
def template():
    app = App()
    stack = NetworkStack(app,"TestStack")
    return Template.from_stack(stack)

#Check if the CIDR range of VPC is "10.0.0.0/16"
def test_vpc_cidr(template):
    template.has_resource_properties("AWS::EC2::VPC",
        Match.object_like({ "CidrBlock" : "10.0.0.0/16" })
    )


@pytest.mark.parametrize("resource,count",[
    #Check if the subnets are created only 2
    ("AWS::EC2::Subnet",2),
    #Check if a subnet group is created 
    ("AWS::RDS::DBSubnetGroup",1)
])

#Check if the subnets are created only 2
def test_resources_count(template,resource,count):
    template.resource_count_is(resource,count)

@pytest.mark.parametrize("service,property,first,second",[
    #Check if both of the subnets are located in defferent A-Z
    ("AWS::EC2::Subnet","AvailabilityZone","ap-northeast-3a","ap-northeast-3b"),
    #Check if each of subnet mask is 24
    ("AWS::EC2::Subnet","CidrBlock","10.0.0.0/24","10.0.1.0/24")
])

def test_defferent_propeties(template,service,property,first,second):
    template.has_resource_properties(service,
        Match.object_like({ property : first })
    )
    template.has_resource_properties(service,
        Match.object_like({ property : second })
    )

#Check if no route to the Internet exists
def test_destination_cidr_block(template):
    template.resource_properties_count_is("AWS::EC2::Route",
        Match.object_like({"DestinationCidrBlock":"0.0.0.0/0"}),
        0
    )
