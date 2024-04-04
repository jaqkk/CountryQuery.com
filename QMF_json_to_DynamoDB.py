import json
import boto3

# Initialize a DynamoDB resource with the specified region
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

# Specify your DynamoDB table name
table_name = 'QMFS_DATA'
table = dynamodb.Table(table_name)

# Path to your JSON file
json_file_path = 'C:\\Users\\Admin\\OneDrive\\Desktop\\QMF_CursorAI.json'

# Read and load the JSON file
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Function to batch write items to DynamoDB
def batch_write(table_name, items):
    table = dynamodb.Table(table_name)
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

# Upload the data to DynamoDB
batch_write(table_name, data_to_upload)

print(f"Uploaded {len(data_to_upload)} items to DynamoDB table '{table_name}'.")