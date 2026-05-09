import aws_cdk as cdk
from aws_cdk import Stack, aws_ec2 as ec2, aws_ssm as ssm, aws_ram as ram
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, workload_account: str, shared_services_account: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Create the CENTRAL VPC pinned to ONE AZ to avoid data transfer cost
        self.vpc = ec2.Vpc(self, "CentralHubVpc",
            # max_azs=1,
            availability_zones=["us-east-1a"],
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public", 
                    subnet_type=ec2.SubnetType.PUBLIC, 
                    cidr_mask=24
                )
            ]
        )
        
        # --- ELITE TAGGING PROTOCOL (FINAL VERSION) ---

        # A. VPC Naming
        cdk.Tags.of(self.vpc).add("Name", "Central-Hub-VPC")

        # B. Deep Resource Tagging (IGW and Route Tables)
        # We use separate counters to ensure distinct numbering in the Console
        rt_index = 1
        for child in self.vpc.node.children:
            # Tag the Internet Gateway
            if isinstance(child, ec2.CfnInternetGateway):
                cdk.Tags.of(child).add("Name", "Central-Hub-IGW")
            
            # Tag Route Tables distinctly (RT-01, RT-02...)
            if isinstance(child, ec2.CfnRouteTable):
                cdk.Tags.of(child).add("Name", f"Central-Public-RT-0{rt_index}")
                rt_index += 1

        # C. Subnets Naming (Subnet-01, Subnet-02...)
        for i, subnet in enumerate(self.vpc.public_subnets):
            cdk.Tags.of(subnet).add("Name", f"Central-Public-Subnet-0{i+1}")

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
