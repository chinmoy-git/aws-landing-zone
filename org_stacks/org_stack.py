import os
from aws_cdk import (
    Stack,
    aws_organizations as orgs,
    aws_cloudwatch as cloudwatch,
)
from constructs import Construct

class OrgStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        org_root_id = os.getenv("ORG_ROOT_ID")

        # 1. Security OU: The Vault (Log-Archive lives here)
        security_ou = orgs.CfnOrganizationalUnit(self, "SecurityOU",
            name="Security",
            parent_id=org_root_id
        )

        # 2. Infrastructure OU: The Hub (Network account lives here)
        infra_ou = orgs.CfnOrganizationalUnit(self, "InfraOU",
            name="Infrastructure",
            parent_id=org_root_id
        )

        # 3. Workloads OU: The Factory (Your RCA Bot & AI Ops live here)
        workloads_ou = orgs.CfnOrganizationalUnit(self, "WorkloadsOU",
            name="Workloads",
            parent_id=org_root_id
        )

        # The 'Debt Sniper' Billing Alarm (Always protect the 1.5L income)
        cloudwatch.Alarm(self, "BillingAlarm",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            threshold=10,
            evaluation_periods=1,
            metric=cloudwatch.Metric(
                namespace="AWS/Billing",
                metric_name="EstimatedCharges",
                dimensions_map={"Currency": "USD"}
            )
        )
