from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from django.contrib.auth import get_user_model  # If used custom user model
from rest_framework.response import Response
from rest_framework.views import APIView, exception_handler

from esgrow_backend.app_serializers import UserSerializer
from esgrow_backend.models import User, EscrowTransactions


class CreateUserView(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny  # Or anon users can't register
    ]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            token, created = Token.objects.get_or_create(user=serializer.instance)
            response_data = {"status": status.HTTP_201_CREATED,
                             "status_description": "CREATED",
                             "errors": {},
                             "data": {'token': token.key,
                                      'username': serializer.data["username"],
                                      'email': serializer.data["email"],
                                      'first_name': serializer.data["first_name"],
                                      'last_name': serializer.data["last_name"]
                                      }}

            return Response(response_data,
                            status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            response_data = {"status": status.HTTP_400_BAD_REQUEST, "status_description": "Bad request",
                             "errors": e.detail,
                             "data": {}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = {"status": status.HTTP_400_BAD_REQUEST, "status_description": "Bad request",
                             "errors": {"exception": [f"${e}"]},
                             "data": {}}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginUserView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            response_data = {"status": status.HTTP_200_OK,
                             "status_description": "OK", "erros": {},
                             "data": {
                                 'token': token.key,
                                 'username': user.username,
                                 "email": user.email,
                                 "first_name": user.first_name,
                                 "last_name": user.last_name,
                             }}
            return Response(response_data, status=status.HTTP_200_OK, )
        except ValidationError as e:
            response_data = {"status": status.HTTP_400_BAD_REQUEST, "status_description": "Bad request",
                             "errors": e.detail,
                             "data": {}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = {"status": status.HTTP_400_BAD_REQUEST, "status_description": "Bad request",
                             "errors": {"exception": [f"${e}"]},
                             "data": {}}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EscrowTransactionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user = User.objects.get(username=request.user.username)
        transactions_from = EscrowTransactions.objects.filter(from_user=user)
        transactions_to = EscrowTransactions.objects.filter(to_user=user)

        response_data = {"status": status.HTTP_200_OK, "status description": "Ok", "data": {
            "from_user": transactions_from,
            "to_user": transactions_to
        }}
        return Response(response_data, status=status.HTTP_200_OK)
