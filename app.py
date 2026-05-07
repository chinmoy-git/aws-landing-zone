#!/usr/bin/env python3
import os
import aws_cdk as cdk

# Importing modular stacks
from org_stacks.org_stack import OrgStack
from security_stacks.log_archive_stack import LogArchiveStack
from network_stacks.network_stack import NetworkStack
from workload_stacks.workload_stack import WorkloadStack

app = cdk.App()

# 1. RETRIEVE ACCOUNT IDS FROM ENVIRONMENT
mgmt_id = os.getenv("MGMT_ACCOUNT_ID")
log_id  = os.getenv("LOG_ARCHIVE_ACCOUNT_ID")
net_id  = os.getenv("NETWORK_ACCOUNT_ID")
work_id = os.getenv("WORKLOAD_ACCOUNT_ID")

# 2. MANAGEMENT ACCOUNT (Governance Hub)
if mgmt_id:
    OrgStack(app, "OrgGovernanceStack", 
        env=cdk.Environment(account=mgmt_id, region="us-east-1")
    )

# 3. LOG-ARCHIVE ACCOUNT (Security Vault)
if log_id:
    LogArchiveStack(app, "LogArchiveCentralStack",
        env=cdk.Environment(account=log_id, region="us-east-1")
    )

# 4. WORKLOAD SHARED INFRASTRUCTURE (The "Highway")
# SCALE NOTE: This name "WorkloadSharedNetwork" is suitable for 1 or 100 apps.
# It is deployed in the Workload account to eliminate cross-account NAT costs.
if work_id:
    NetworkStack(app, "WorkloadSharedNetwork", 
        env=cdk.Environment(account=work_id, region="us-east-1")
    )

# 5. NETWORKING ACCOUNT (The Global Control Tower)
# This stays in the Networking account for future Transit Gateway/VPN tools.
if net_id:
    NetworkStack(app, "GlobalControlNetworkMumbai", 
        env=cdk.Environment(account=net_id, region="ap-south-1")
    )

# 6. WORKLOAD APP BASELINE (Identity & Permissions)
if work_id:
    WorkloadStack(app, "WorkloadAccountBaseline",
        env=cdk.Environment(account=work_id, region="us-east-1")
    )

app.synth()
