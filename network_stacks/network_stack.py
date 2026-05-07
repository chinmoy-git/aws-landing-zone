from aws_cdk import Stack, aws_ec2 as ec2, aws_ssm as ssm
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Create the Shared VPC with PUBLIC SUBNETS ONLY (Zero NAT cost)
        self.vpc = ec2.Vpc(self, "SharedWorkloadVpc",
            max_azs=2,
            nat_gateways=0, # Protects your ₹5,100 buffer
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                )
            ]
        )

        # 2. Add an S3 Gateway Endpoint (FREE)
        # This is the "Backdoor" to her school books in S3
        self.vpc.add_gateway_endpoint("S3Endpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3
        )

        # 3. Export the VPC ID to the SSM Parameter Store
        # This is the "Signpost" for the Bidya app repo to find
        ssm.StringParameter(self, "VpcIdParam",
            parameter_name="/platform/network/workload-vpc-id",
            string_value=self.vpc.vpc_id,
            description="The VPC ID for the Bidya Knowledge Engine"
        )
