from rest_custom.serializers import BaseSerializer, ModelSerializer
from rest_framework.serializers import Field
from users.models import Users, session
from django.utils.html import escape
from datetime import datetime

class TimestampField(Field):
    '''Replace original datatime format to timestamp format'''
    def to_native(self, value):
        epoch = datetime(1970,1,1)
        return int((value - epoch).total_seconds())

    def to_representation(self, value):
        return int(value.timestamp()) * 1000

class UsersSerializer(ModelSerializer, BaseSerializer):   
    created_at = TimestampField(required=False)
    updated_at = TimestampField(required=False)
    
    class Meta:
        '''For security reason, password field is strictly recommended not to show-up'''
        model = Users
        session = session
        fields = ['acct', 'fullname', 'created_at', 'updated_at']