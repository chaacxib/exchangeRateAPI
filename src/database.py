from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute


class User(Model):
    """
    A DynamoDB User
    """
    class Meta:
        table_name = 'dynamodb-user'
        region = 'us-east-1'

    username = UnicodeAttribute(hash_key=True)
    hashed_password = UnicodeAttribute()


class Request(Model):

    class Meta:
        table_name = 'dynamodb-request'
        region = 'us-east-1'

    username = UnicodeAttribute(hash_key=True)
    datetime = UTCDateTimeAttribute(range_key=True)
