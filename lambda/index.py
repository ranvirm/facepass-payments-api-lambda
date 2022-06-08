from json import loads, dumps
# import os
from boto3 import resource, client
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
from time import time
from datetime import datetime, timedelta
from uuid import uuid4
from decimal import Decimal
import stripe


# configure stripe
stripe.api_key = "sk_test_51ILndFHaEYRIaDnRIURSZhbLCwIp6tUsqiJNSqHjsvtXG8ffwxE82WBT00ELHvDa8UZKp3pNLtM1vk70o39X5kHX00aLmBLJc8"



"""
RESOURCES
"""



"""
END RESOURCES
"""


"""
RESPONSE MESSAGES
"""


def error_400_msg(error=None):
    msg = {
        'statusCode': 400,
        'body': dumps(
            {
                'error': {'type': 'REQUEST_FAILED', 'desc': 'generic error'} if error is None else error
            }
        )
    }
    return msg


def success_200_msg(body=None):
    msg = {
        'statusCode': 200,
        'body': dumps(body)
    }
    return msg


def success_201_msg(body=None):
    msg = {
        'statusCode': 201,
        'body': dumps(body)
    }
    return msg


"""
END RESPONSE MESSAGES
"""


"""
UTILS
"""


def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


"""
END UTILS
"""

"""
QUERY PATH HANDLERS
"""


def create_payment_sheet(event):

    customer = stripe.Customer.create()
    ephemeralKey = stripe.EphemeralKey.create(
        customer=customer['id'],
        stripe_version='2020-08-27',
    )
    paymentIntent = stripe.PaymentIntent.create(
        amount=1099,
        currency='usd',
        customer=customer['id'],
        automatic_payment_methods={
            'enabled': True,
        },
    )

    body = {
        "paymentIntent": paymentIntent.client_secret,
        "ephemeralKey": ephemeralKey.secret,
        "customer": customer.id
    }

    return success_200_msg(body=body)



"""
END QUERY PATH HANDLERS
"""

"""
CONSTANTS
"""


def query_path_router(event):
    paths = {
        'create_payment_sheet': create_payment_sheet
    }
    return paths[event['queryStringParameters']['action']](event)


path_handlers = {
    '/main': {
        'POST': query_path_router
    },

}


"""
END CONSTANTS
"""


"""
MAIN EVENT HANDLER
"""


def lambda_handler(event, context):
    try:
        print(event)

        # route request to function
        response = path_handlers[event['path']][event['httpMethod']](event)

        return response
    except Exception as e:
        return error_400_msg(error=e.__str__())
