import aws_cdk as cdk
from aws_cdk import Stack, aws_ec2 as ec2, aws_ssm as ssm, aws_ram as ram
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, workload_account: str, shared_services_account: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Create the CENTRAL VPC
        # We explicitly name the VPC so it shows up as "Central-Hub-VPC" in the Console
        self.vpc = ec2.Vpc(self, "CentralHubVpc",
            max_azs=2,
            nat_gateways=0, # Protects your ₹5,100 debt-clearing buffer
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public", 
                    subnet_type=ec2.SubnetType.PUBLIC, 
                    cidr_mask=24
                )
            ]
        )
        # ELITE MOVE: Add Name tag to the VPC itself
        cdk.Tags.of(self.vpc).add("Name", "Central-Hub-VPC")

        # 2. Add S3 Gateway Endpoint (Free)
        # We capture this in a variable to apply naming tags
        s3_endpoint = self.vpc.add_gateway_endpoint("S3Endpoint", 
            service=ec2.GatewayVpcEndpointAwsService.S3
        )
        # ELITE MOVE: Give the endpoint a professional label in the Console
        cdk.Tags.of(s3_endpoint).add("Name", "Central-S3-Gateway-Endpoint")

        # 3. THE HUB & SPOKE HANDSHAKE
        principals = [shared_services_account]
        if workload_account and workload_account not in ["None", "000000000000"]:
            principals.append(workload_account)

        ram.CfnResourceShare(self, "SubnetShare",
            name="CentralNetworkShare",
            allow_external_principals=False,
            principals=principals,
            # We manually construct the ARN because subnet.subnet_arn is not a valid CDK attribute
            resource_arns=[
                f"arn:aws:ec2:{self.region}:{self.account}:subnet/{subnet.subnet_id}" 
                for subnet in self.vpc.public_subnets
            ]
        )

        # 4. Export the VPC ID to SSM (Signpost for the App repos)
        ssm.StringParameter(self, "VpcIdParam",
            parameter_name="/platform/network/central-vpc-id",
            string_value=self.vpc.vpc_id,
            description="Central Hub VPC ID shared via RAM"
        )
