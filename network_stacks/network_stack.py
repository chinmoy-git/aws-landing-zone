import aws_cdk as cdk
from aws_cdk import Stack, aws_ec2 as ec2, aws_ssm as ssm, aws_ram as ram
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, workload_account: str, shared_services_account: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Create the CENTRAL VPC
        self.vpc = ec2.Vpc(self, "CentralHubVpc",
            max_azs=2,
            nat_gateways=0, # Crucial: Protects your ₹5,100 buffer
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public", 
                    subnet_type=ec2.SubnetType.PUBLIC, 
                    cidr_mask=24
                )
            ]
        )
        
        # --- ELITE TAGGING PROTOCOL ---

        # A. VPC Naming
        cdk.Tags.of(self.vpc).add("Name", "Central-Hub-VPC")

        # B. Internet Gateway (IGW) Naming
        # CDK creates this automatically. We find it in the VPC's children and tag it.
        # This is a "Senior Architect" move to ensure console clarity.
        for child in self.vpc.node.children:
            if isinstance(child, ec2.CfnInternetGateway):
                cdk.Tags.of(child).add("Name", "Central-Hub-IGW")

        # C. Subnets & Route Tables Naming
        # We loop through the generated subnets to give them professional names
        for i, subnet in enumerate(self.vpc.public_subnets):
            # Tag the Subnet
            cdk.Tags.of(subnet).add("Name", f"Central-Public-Subnet-0{i+1}")
            
            # Tag the Route Table associated with this subnet
            # Usually, public subnets share one RT when there is no NAT Gateway
            if subnet.route_table:
                cdk.Tags.of(subnet.route_table).add("Name", "Central-Public-RT")

        # 2. Add S3 Gateway Endpoint (Free)
        s3_endpoint = self.vpc.add_gateway_endpoint("S3Endpoint", 
            service=ec2.GatewayVpcEndpointAwsService.S3
        )
        
        # D. S3 Endpoint Naming
        cdk.Tags.of(s3_endpoint).add("Name", "Central-S3-Gateway-Endpoint")

        # 3. THE HUB & SPOKE HANDSHAKE (RAM)
        principals = [shared_services_account]
        if workload_account and workload_account not in ["None", "000000000000"]:
            principals.append(workload_account)

        ram.CfnResourceShare(self, "SubnetShare",
            name="CentralNetworkShare",
            allow_external_principals=False,
            principals=principals,
            resource_arns=[
                f"arn:aws:ec2:{self.region}:{self.account}:subnet/{subnet.subnet_id}" 
                for subnet in self.vpc.public_subnets
            ]
        )

        # 4. Export the master VPC ID to SSM
        ssm.StringParameter(self, "VpcIdParam",
            parameter_name="/platform/network/central-vpc-id",
            string_value=self.vpc.vpc_id,
            description="The master VPC ID for the Hub-and-Spoke network"
        )
