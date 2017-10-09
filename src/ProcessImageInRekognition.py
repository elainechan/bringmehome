from __future__ import print_function

import boto3
from decimal import Decimal
import json
import urllib

#Python 2.7

print('Loading function')

rekognition = boto3.client('rekognition')
lambda_client = boto3.client('lambda')


# --------------- Helper Functions to call Rekognition APIs ------------------

def detect_labels(bucket, key):
    response = rekognition.detect_labels(Image={"S3Object": {"Bucket": bucket, "Name": key}})

    # Sample code to write response to DynamoDB table 'MyTable' with 'PK' as Primary Key.
    # Note: role used for executing this Lambda function should have write access to the table.
    #table = boto3.resource('dynamodb').Table('MyTable')
    #labels = [{'Confidence': Decimal(str(label_prediction['Confidence'])), 'Name': label_prediction['Name']} for label_prediction in response['Labels']]
    #table.put_item(Item={'PK': key, 'Labels': labels})
    return response



# --------------- Main handler ------------------


def lambda_handler(event, context):
    '''Demonstrates S3 trigger that uses
    Rekognition APIs to detect faces, labels and index faces in S3 Object.
    '''
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('BringMeHome')

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    guid = key[:-4]

    try:

        # Calls rekognition DetectLabels API to detect labels in S3 object
        response = detect_labels(bucket, key)

        # Print response to console.
        print('key: %s' % key)

        labels = {'Labels': response['Labels']}
        # Get breed from labels
        lambda_response = json.loads(lambda_client.invoke(
            FunctionName='getBreedsFromRekognition',
            InvocationType='RequestResponse',
            Payload=json.dumps(labels)
        )['Payload'].read())

        print(lambda_response)
        breed = lambda_response['breed']

        #update DynamoDB
        response = table.update_item(
            Key={'id': guid },
            UpdateExpression="set breed=:b",
            ExpressionAttributeValues={
                ':b': breed
            },
            ReturnValues="UPDATED_NEW"
        )


        return response
    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}. ".format(key, bucket) +
              "Make sure your object and bucket exist and your bucket is in the same region as this function.")
        raise e


# def parseResponse(response):
