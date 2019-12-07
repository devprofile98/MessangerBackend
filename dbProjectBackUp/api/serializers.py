from rest_framework.serializers import ModelSerializer
# from django.contrib.auth.models import User
from registration.models import User
from realtime.models import pvChat,profile




class UserGroupSerializers(ModelSerializer):
    class Meta:
        model = pvChat
        fields = [
            'id',
            'pv_name',
            'last_activity',
        ]

class CreateUserProfileApi(ModelSerializer):

    # def create(self, validated_data):
    #     return super().create(validated_data)

    class Meta:
        model = profile
        fields = [
            'owner',
            'biography',
            'firstname',
            'lastname',
        ]