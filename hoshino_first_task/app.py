#!/usr/bin/env python3
import os

import aws_cdk as cdk

from first_task.first_task_stack import FirstTaskStack
from first_task.database_stack import DatabaseStack

app = cdk.App()

env = cdk.Environment(
    account = os.environ["CDK_DEFAULT_ACCOUNT"], #"338071012882", 
    region = "ap-northeast-3"
) 

DatabaseStack(app,"DatabaseStack",env=env)

app.synth()
