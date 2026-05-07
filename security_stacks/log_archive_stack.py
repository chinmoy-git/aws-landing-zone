from aws_cdk import (
    Stack,
)
from constructs import Construct


class LogArchiveStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # We will add S3 Bucket logic here later
