import aws_cdk as cdk
import os
from aws_cdk import integ_tests_alpha as integ
from aws_cdk.assertions import Match

from cwd_fix import fix_cwd
fix_cwd()

from first_task.database_stack import DatabaseStack
from first_task.network_stack import NetworkStack

app = cdk.App()
env = cdk.Environment(
    account = "338071012882", #os.environ["CDK_DEFAULT_ACCOUNT"],
    region = "ap-northeast-3"
)
network = NetworkStack(app,"TestNetworkStack")
database = DatabaseStack(app,"DatabaseStack",network.vpc,network.subnet_group)

test = integ.IntegTest(app,"Integ",test_cases=[stack])

#Get information regarding DBCluster Endpoint
check_cluster_endpoint=test.assertions.aws_api_call(
    service="RDS",
    api="describeDBClusterEndpoints"
)

#Get information regarding DBInstances
check_db_instance_endpoints=test.assertions.aws_api_call(
    service="RDS",
    api="describeDBInstances"
)

#Check if the cluster endpoint is decided
check_cluster_endpoint.expect(
    integ.ExpectedResult.object_like(
        {"Endpoint": Match.any_value()}
    )
)

check_dict_list = [
    #Check if the instance endpoint is decided
    {"Endpoint": Match.any_value()},
    #Check one of DBinstances is in the first A-Z
    {"AvailabilityZone":"ap-northeast-3a"},
    #Check one of DBinstances is in the second A-Z
    {"AvailabilityZone":"ap-northeast-3b"}
]

for item in check_dict_list:
    check_db_instance_endpoints.expect(
        integ.ExpectedResult.object_like(item)
    )


app.synth()