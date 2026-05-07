#!/usr/bin/env python3
import os
import aws_cdk as cdk

# Importing modular stacks
from org_stacks.org_stack import OrgStack
from security_stacks.log_archive_stack import LogArchiveStack
from network_stacks.network_stack import NetworkStack
from workload_stacks.workload_stack import WorkloadStack

app = cdk.App()

# 1. RETRIEVE ALL IDENTIFIERS FROM ENVIRONMENT
mgmt_id = os.getenv("MGMT_ACCOUNT_ID")
log_id  = os.getenv("LOG_ARCHIVE_ACCOUNT_ID")
net_id  = os.getenv("NETWORK_ACCOUNT_ID")
work_id = os.getenv("WORKLOAD_ACCOUNT_ID")
org_root_id = os.getenv("ORG_ROOT_ID") # <--- THE MISSING LINK

# 2. MANAGEMENT ACCOUNT (Governance)
# We only deploy this if we have the Account ID AND the Org Root ID
if mgmt_id and org_root_id:
    OrgStack(app, "OrgGovernanceStack", 
        org_root_id=org_root_id,
        env=cdk.Environment(account=mgmt_id, region="us-east-1")
    )
elif mgmt_id:
    print("Warning: MGMT_ACCOUNT_ID found but ORG_ROOT_ID is missing. Skipping OrgGovernanceStack.")

# 3. LOG-ARCHIVE ACCOUNT (Security)
if log_id:
    LogArchiveStack(app, "LogArchiveCentralStack",
        env=cdk.Environment(account=log_id, region="us-east-1")
    )

# 4. WORKLOAD SHARED NETWORK (The Highway)
if work_id:
    NetworkStack(app, "WorkloadSharedNetwork", 
        env=cdk.Environment(account=work_id, region="us-east-1")
    )

# 5. NETWORKING (Mumbai Control Tower)
if net_id:
    NetworkStack(app, "GlobalControlNetworkMumbai", 
        env=cdk.Environment(account=net_id, region="ap-south-1")
    )

# 6. WORKLOAD BASELINE
if work_id:
    WorkloadStack(app, "WorkloadAccountBaseline",
        env=cdk.Environment(account=work_id, region="us-east-1")
    )

app.synth()
