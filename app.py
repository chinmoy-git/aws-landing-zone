#!/usr/bin/env python3
import os
import aws_cdk as cdk
from org_stacks.org_stack import OrgStack

app = cdk.App()

# THE ARCHITECT'S MOVE: Injecting secrets via Environment Variables
mgmt_account = os.getenv("MGMT_ACCOUNT_ID")

if mgmt_account:
    OrgStack(app, "OrgStack", 
        env=cdk.Environment(account=mgmt_account, region="us-east-1")
    )
else:
    print("Warning: MGMT_ACCOUNT_ID not found. Local synthesis only.")

app.synth()
