import os
from aws_cdk import Stack, aws_organizations as orgs
from constructs import Construct

class OrgStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Retrieve the Root ID from environment variables (GitHub Secrets)
        org_root_id = os.getenv("ORG_ROOT_ID")

        # Create the OUs
        security_ou = orgs.CfnOrganizationalUnit(self, "SecurityOU",
            name="Security",
            parent_id=org_root_id
        )
        # ... add Infra and Workload OUs here similarly
