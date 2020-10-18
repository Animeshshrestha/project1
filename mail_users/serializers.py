import datetime
from rest_framework import serializers, status

from .models import UserEmail, CustomUser

class UserEmailSerailizer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='email')

    class Meta:
        model = CustomUser
        fields = ('user_email',)

class EmailListSerializer(serializers.ModelSerializer):

    sender = serializers.ReadOnlyField(source='sender.email')
    receiver = UserEmailSerailizer(read_only=True, many=True)
    # receiver = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)
    class Meta:
        model = UserEmail
        fields = ['id','sender','receiver','subject','message_text','created_at','is_read','is_archived']