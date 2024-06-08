from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from drf_dynamic_read.views import DynamicReadViewMixin
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from myapp.models import User, FriendRequest
from myapp.serializers import UserSerializer, LoginSerializer, FriendRequestSerializer


class NoActionsPermission(BasePermission):
    def has_permission(self, request, view):
        if (
            hasattr(view, "actions_not_allowed")
            and view.action in view.actions_not_allowed
        ):
            return False
        else:
            return True


class BaseViewSet(DynamicReadViewMixin, viewsets.ModelViewSet):
    permission_classes = (NoActionsPermission, IsAuthenticated)


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    actions_not_allowed = ["create", "update", "destroy", "partial_update", "list", "retrieve"]

    @action(detail=False, methods=["post"], permission_classes=[AllowAny], authentication_classes=[],
            serializer_class=UserSerializer)
    def sign_up(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, filter_fields=["first_name", "last_name", "email"])
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=(AllowAny,),
        authentication_classes=(),
        serializer_class=LoginSerializer,
    )
    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = authenticate(
            email=data["email"].lower(), password=data["password"]
        )
        if not user:
            return Response("Invalid credentials", status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"])
    def logout(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def search_user(self, request, *args, **kwargs):
        keyword = request.query_params.get("search")
        if not keyword:
            return Response("Please provide a keyword to search", status=status.HTTP_400_BAD_REQUEST)
        users = self.get_queryset().filter(email=keyword)
        if not users.exists():
            users = self.get_queryset().filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword))
        users = self.paginate_queryset(users)
        serializer = self.serializer_class(users, many=True, filter_fields=["first_name", "last_name", "email", "id"])
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["GET"])
    def get_friends(self, request, *args, **kwargs):
        friends = request.user.friends.all()
        friends = self.paginate_queryset(friends)
        serializer = self.serializer_class(friends, many=True, filter_fields=["first_name", "last_name", "email", "id"])
        return self.get_paginated_response(serializer.data)


class RequestViewSet(BaseViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    actions_not_allowed = ["create", "update", "destroy", "partial_update", "list", "retrieve"]

    @action(detail=False, methods=["POST"], throttle_classes=[UserRateThrottle])
    def send_request(self, request, *args, **kwargs):
        data = request.data
        data["from_user_id"] = request.user.id
        serializer = self.serializer_class(data=data, filter_fields=["to_user_id", "from_user_id"])
        serializer.is_valid(raise_exception=True)
        if FriendRequest.objects.filter(
                from_user=request.user, to_user_id=serializer.validated_data["to_user"]).exists():
            return Response("Request already sent", status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response("Request successfully sent", status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def get_requests(self, request, *args, **kwargs):
        requests = self.get_queryset().filter(to_user=request.user, accepted=False)
        requests = self.paginate_queryset(requests)
        serializer = self.serializer_class(requests, many=True, filter_fields=["from_user", "id"])
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["POST"])
    def cancel_request(self, request, *args, **kwargs):
        request_obj = self.get_object()
        if request_obj.to_user != request.user:
            return Response("You are not allowed to cancel this request", status=status.HTTP_400_BAD_REQUEST)
        request_obj.delete = True
        request_obj.save()
        return Response("Request rejected", status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def accept_request(self, request, *args, **kwargs):
        request_obj = self.get_object()
        if request_obj.to_user != request.user:
            return Response("You are not allowed to accept this request", status=status.HTTP_400_BAD_REQUEST)
        if request_obj.accepted:
            return Response("Friend Request already accepted", status=status.HTTP_400_BAD_REQUEST)
        request_obj.accepted = True
        request_obj.save()
        request_obj.from_user.friends.add(request_obj.to_user)
        request_obj.to_user.friends.add(request_obj.from_user)
        return Response("Request accepted", status=status.HTTP_200_OK)
