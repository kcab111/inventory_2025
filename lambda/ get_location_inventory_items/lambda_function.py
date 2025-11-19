import json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from decimal import Decimal

# DynamoDB setup
# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Define the DynamoDB table name
TABLE_NAME = 'Inventory'
GSI_NAME = 'GSI_SK_PK'


# Function to convert Decimal to int/float
def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):  
        return int(obj) if obj % 1 == 0 else float(obj)  # Convert to int if whole number, else float
    return obj


def lambda_handler(event, context):
    table = dynamodb.Table(TABLE_NAME)

    # Get the key from the path parameters
    if 'pathParameters' not in event or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }

    key_value = event['pathParameters']['id']

    table = dynamodb.Table(TABLE_NAME)

    try:
        # Query to get all items with PK = "Location1" and SK begins with "Rabbit"
        response = table.query(
            IndexName=GSI_NAME,
            KeyConditionExpression=Key('location_id').eq(int(key_value))
        )
        items = response.get('Items', [])

        # Convert Decimal values to JSON serializable types
        items = convert_decimals(items)
    except ClientError as e:
        print(f"Failed to query items: {e.response['Error']['Message']}")
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to query items')
        }

    return {
        'statusCode': 200,
        'body': json.dumps(items)
    }
