from aws_cdk import (
    Stack,
    aws_cloudwatch as cloudwatch,
)
from constructs import Construct

class AwsLandingZoneStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1% Strategy: First resource is ALWAYS a billing alarm
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
