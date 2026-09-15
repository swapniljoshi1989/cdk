"""
Since the environment in this instance falls within the free tier, 
the `WithExpressConfiguration` setting was mandatory to run the Aurora engine; 
however, because CloudFormation does not support this setting, 
the deployment for this integration test fails.
"""

#!/usr/bin/env python3
import json

import aws_cdk as cdk
from aws_cdk import integ_tests_alpha as integ

from cwd_fix import fix_cwd
fix_cwd()

from first_task.database_stack import DatabaseStack


app = cdk.App()
stack = DatabaseStack(app,"IntegTestBucket")

integ_test = integ.IntegTest(app,"IntegTest",test_cases = [stack])

#Test whether administrator information is stored using Secret Manager.
api_result = integ_test.assertions.aws_api_call(
    "SecretsManager",
    "getSecretValue",
    {
        "SecretId": stack.credentials.secret_arn,
    },
)

#Verify that the dbadmin data is saved.
api_result.expect(integ.ExpectedResult.object_like({
    "username": "dbadmin"
}))


app.synth()




