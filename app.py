#!/usr/bin/env python3
import os
import aws_cdk as cdk

# Importing your modular stacks from their respective directories
from org_stacks.org_stack import OrgStack
from security_stacks.log_archive_stack import LogArchiveStack
from network_stacks.network_stack import NetworkStack
from shared_services_stacks.shared_services_stack import SharedServicesStack
from workload_stacks.workload_stack import WorkloadStack

app = cdk.App()

# 1. RETRIEVE ACCOUNT IDS FROM ENVIRONMENT (GitHub Secrets / Local Env)
# This prevents exposing your private IDs in your public GitHub repo.
mgmt_id = os.getenv("MGMT_ACCOUNT_ID")
log_id  = os.getenv("LOG_ARCHIVE_ACCOUNT_ID")
net_id  = os.getenv("NETWORK_ACCOUNT_ID")
ss_id  = os.getenv("SHARED_SERVICES_ACCOUNT_ID")
work_id = os.getenv("WORKLOAD_ACCOUNT_ID")

# 2. MANAGEMENT ACCOUNT (Virginia - The Governance Hub)
# Must be Virginia to monitor Global Billing Alarms (The Debt Sniper).
if mgmt_id:
    OrgStack(app, "OrgStack", 
        env=cdk.Environment(account=mgmt_id, region="us-east-1")
    )

# 3. LOG-ARCHIVE ACCOUNT (Virginia - The Security Vault)
# Virginia offers the most cost-effective S3 storage for your audit logs.
if log_id:
    LogArchiveStack(app, "LogArchiveStack",
        env=cdk.Environment(account=log_id, region="us-east-1")
    )

# # 4. NETWORKING ACCOUNT (Mumbai - Personal Speed)
# # We deploy networking here so your test instances feel fast from Kolkata.
# if net_id:
#     NetworkStack(app, "NetworkMumbai", 
#         env=cdk.Environment(account=net_id, region="ap-south-1")
#     )

# 5. NETWORKING ACCOUNT SHARED NETWORK (Virginia)
# STRATEGIC MOVE: Deployed in NETWORKING ACCOUNT to shared resources.
if net_id:
    NetworkStack(app, "NetworkStack",
        shared_services_account=str(ss_id),
        workload_account=str(work_id),
        env=cdk.Environment(account=net_id, region="us-east-1")
    )

# 6. WORKLOAD ACCOUNT (Virginia - The AI Engine)
# Virginia is the hub for Amazon Bedrock and the newest AI models.
if work_id:
    WorkloadStack(app, "WorkloadStack",
        env=cdk.Environment(account=work_id, region="us-east-1")
    )

# 6. Shared Services ACCOUNT (Virginia)
# Virginia is the hub for Shared Services.
if ss_id:
    WorkloadStack(app, "SharedServicesStack",
        env=cdk.Environment(account=ss_id, region="us-east-1")
    )

app.synth()
