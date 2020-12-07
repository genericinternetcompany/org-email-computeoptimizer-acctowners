import json
import boto3

def lambda_handler(event, context):
    
    client = boto3.client('compute-optimizer')
    response = client.export_ec2_instance_recommendations(
        s3DestinationConfig={
            'bucket': 'recommendation-compute-ec2',
            'keyPrefix': '/'
        },
        
        fileFormat= 'Csv',
        includeMemberAccounts=True
    )
    
    return response