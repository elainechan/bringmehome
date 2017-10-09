import boto3

# Python 3.6

s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('BringMeHome')
def handler(event, context):
    id = '887d6cd5-cbf8-4c88-a14e-ce36fbd1cc0e'


    #if request['Status'] == 'Lost'
    table.update_item(
        Key={'id': id },
        UpdateExpression="set PetStatus=:b",
        ExpressionAttributeValues={
            ':b': 'Found'
        },
        ReturnValues="UPDATED_NEW"
    )

    request = table.get_item(
        Key={
            'id': id
        }
    )
    phone = str(request['Item']['OwnerPhone'])
    phone = '+1' + phone
    print(phone)
    message = 'We received your notification that ' + request['Item']['PetName'] + ' was found'
    sns = boto3.client('sns')
    sns.publish(
        PhoneNumber = phone,
        Message = message
    )
    return None
