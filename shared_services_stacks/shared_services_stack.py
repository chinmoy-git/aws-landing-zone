from aws_cdk import (
    Stack,
)
from constructs import Construct

class SharedServicesStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # We will logic here later
