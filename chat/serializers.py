from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from chat.models import ChatRoom, ChatRoomMembership, MessageModel
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField

class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)

class ChatRoomUserSerializer(ModelSerializer):
    user = SerializerMethodField()

    class Meta:
        model = ChatRoomMembership
        fields = ('user',)

    def get_user(self, obj):
        return obj.user.username
    
class ChatRoomNameSerializer(ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ('name',)

class MessageModelSerializer(ModelSerializer):
    user = CharField(source='user.username', read_only=True)
    recipient = CharField(source='recipient.username')

    def create(self, validated_data):
        user = self.context['request'].user
        recipient = get_object_or_404(
            User, username=validated_data['recipient']['username'])
        msg = MessageModel(recipient=recipient,
                           body=validated_data['body'],
                           user=user)
        msg.save()
        return msg

    class Meta:
        model = MessageModel
        fields = ('id', 'user', 'recipient', 'timestamp', 'body')

