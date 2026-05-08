from aws_cdk import Stack, aws_ec2 as ec2, aws_ssm as ssm, aws_ram as ram
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, workload_account: str, shared_services_account: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Create the CENTRAL VPC in the Network Account
        self.vpc = ec2.Vpc(self, "CentralHubVpc",
            max_azs=2,
            nat_gateways=0, 
            subnet_configuration=[
                ec2.SubnetConfiguration(name="Public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24)
            ]
        )

        # 2. Add S3 Gateway Endpoint (Free)
        self.vpc.add_gateway_endpoint("S3Endpoint", service=ec2.GatewayVpcEndpointAwsService.S3)

        # 3. THE HUB & SPOKE HANDSHAKE
        # Prepare the list of accounts that can "see" this road
        principals = [shared_services_account]
        if workload_account and workload_account != "None":
            principals.append(workload_account)

        ram.CfnResourceShare(self, "SubnetShare",
            name="CentralNetworkShare",
            allow_external_principals=False,
            principals=principals,
            # ELITE FIX: We manually construct the ARN because subnet.subnet_arn doesn't exist
            resource_arns=[
                f"arn:aws:ec2:{self.region}:{self.account}:subnet/{subnet.subnet_id}" 
                for subnet in self.vpc.public_subnets
            ]
        )

        # 4. Export the VPC ID to SSM (In the Network Account)
        ssm.StringParameter(self, "VpcIdParam",
            parameter_name="/platform/network/central-vpc-id",
            string_value=self.vpc.vpc_id
        )
