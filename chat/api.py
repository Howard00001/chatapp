from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from django.db.models import Q

from chat.serializers import UserModelSerializer, ChatRoomNameSerializer, ChatRoomUserSerializer, MessageModelSerializer
from chat.models import ChatRoom, ChatRoomMembership, MessageModel


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication scheme used by DRF. DRF's SessionAuthentication uses
    Django's session framework for authentication which requires CSRF to be
    checked. In this case we are going to disable CSRF tokens for the API.
    """

    def enforce_csrf(self, request):
        return

class MessagePagination(PageNumberPagination):
    """
    Limit message prefetch to one page.
    """
    page_size = 15

class UserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserModelSerializer
    allowed_methods = ('GET', 'HEAD', 'OPTIONS')
    pagination_class = None  # Get all user

    def list(self, request, *args, **kwargs):
        # Get all users except yourself
        self.queryset = self.queryset.exclude(id=request.user.id)
        return super(UserModelViewSet, self).list(request, *args, **kwargs)
    
class ChatRoomModelViewSet(ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomNameSerializer
    allowed_methods = ('GET', 'HEAD', 'OPTIONS')
    pagination_class = None  # Get all Room

    def list(self, request, *args, **kwargs):
        return super(ChatRoomModelViewSet, self).list(request, *args, **kwargs)
    
class ChatRoomUserModelViewSet(ModelViewSet):
    queryset = ChatRoomMembership.objects.all()
    serializer_class = ChatRoomUserSerializer
    allowed_methods = ('GET', 'HEAD', 'OPTIONS')
    pagination_class = None  # Get all Room

    def list(self, request, *args, **kwargs):
        room_name = request.query_params.get('room_name', None)

        # Filter the queryset to get usernames from ChatRoomMembership for the current chat room
        self.queryset = ChatRoomMembership.objects.filter(chat_room=room_name)
        self.queryset = self.queryset.exclude(user=request.user)
        return super(ChatRoomUserModelViewSet, self).list(request, *args, **kwargs)
    
class MessageModelViewSet(ModelViewSet):
    queryset = MessageModel.objects.all()
    serializer_class = MessageModelSerializer
    allowed_methods = ('GET', 'POST', 'HEAD', 'OPTIONS')
    authentication_classes = (CsrfExemptSessionAuthentication,)
    pagination_class = MessagePagination

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(Q(recipient=request.user) |
                                             Q(user=request.user))
        target = self.request.query_params.get('target', None)
        if target is not None:
            self.queryset = self.queryset.filter(
                Q(recipient=request.user, user__username=target) |
                Q(recipient__username=target, user=request.user))
        return super(MessageModelViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        msg = get_object_or_404(
            self.queryset.filter(Q(recipient=request.user) |
                                 Q(user=request.user),
                                 Q(pk=kwargs['pk'])))
        serializer = self.get_serializer(msg)
        return Response(serializer.data)
