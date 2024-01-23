import uuid
import datetime
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from rest_framework import permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from django.contrib.auth import get_user_model  # If used custom user model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from esgrow_backend.app_serializers import EscrowTransactionSerializer, EscrowViewTransactionSerializer, \
    LoggedInUserSerializer, UserSerializer
from esgrow_backend.models import User, EscrowTransactions, TransactionStage


class CreateUserView(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny  # Or anon users can't register
    ]
    serializer_class = LoggedInUserSerializer

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
                             "data": {'auth_token': token.key,
                                      "id": serializer.data["id"],
                                      'username': serializer.data["username"],
                                      'email': serializer.data["email"],
                                      'first_name': serializer.data["first_name"],
                                      'last_name': serializer.data["last_name"],
                                      'balance': serializer.data["balance"],
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
            user: User = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            response_data = {"status": status.HTTP_200_OK,
                             "status_description": "OK", "errors": {},
                             "data": {
                                 'auth_token': token.key,
                                 'id': user.id,
                                 'username': user.username,
                                 "email": user.email,
                                 "first_name": user.first_name,
                                 "last_name": user.last_name,
                                 "balance": user.balance
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

    serializer_class = EscrowViewTransactionSerializer

    def get(self, request):
        user = User.objects.get(username=request.user.username)
        transactions_from = EscrowTransactions.objects.filter(from_user=user).prefetch_related("from_user")
        transactions_to = EscrowTransactions.objects.filter(to_user=user).prefetch_related("to_user")

        transactions_from_serialized = self.serializer_class(transactions_from, many=True)
        transactions_to_serialized = self.serializer_class(transactions_to, many=True)

        response_data = {"status": status.HTTP_200_OK,
                         "status description": "Ok",
                         "errors": {},
                         "data": {
                             "from_user": transactions_from_serialized.data,
                             "to_user": transactions_to_serialized.data
                         }}
        return Response(response_data, status=status.HTTP_200_OK)


class EscrowTransactionAddView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EscrowTransactionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
            if serializer.data['from_user'] != request.user.id or serializer.data['to_user'] != request.user.id:
                response_data = {"status": status.HTTP_400_BAD_REQUEST, "status_description": "Bad request",
                                 "errors": [{"user_id": "Logged in user is not part of the transaction"}],
                                 "data": {}}
                return Response(status=status.HTTP_400_BAD_REQUEST, data=response_data)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            response_data = {"status": status.HTTP_400_BAD_REQUEST, "status_description": "Bad request",
                             "errors": e.detail,
                             "data": {}}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def confirm_transaction(request, transaction_id: uuid.UUID):
    transaction = EscrowTransactions.objects.get(transaction_id=transaction_id)
    if transaction is None:
        response_data = {"status": status.HTTP_404_NOT_FOUND,
                         "status_description": "NOT FOUND",
                         "errors": {
                             "transaction_id": ["Transaction wasn't found"]
                         },
                         "data": {}}
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)

    user: User = request.user

    if user is None:
        raise ValidationError("User not found")
    if not request.user.is_authenticated:
        raise ValidationError("User is not authenticated")

    if user == transaction.from_user:
        transaction.from_user_confirmed = True
        transaction.from_user_confirmed_date = datetime.datetime.now()
        transaction.save()
    elif user == transaction.to_user:
        transaction.to_user_confirmed = True
        transaction.to_user_confirmed_date = datetime.datetime.now()
        transaction.save()
    else:
        response_data = {"status": status.HTTP_400_BAD_REQUEST,
                         "status_description": "BAD REQUEST",
                         "errors": {
                             "user_id": ["Logged In user is not part of the transaction"]
                         },
                         "data": {}}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    serializer = EscrowViewTransactionSerializer(transaction, many=False)

    response_data = {"status": status.HTTP_200_OK,
                     "status_description": "OK",
                     "errors": [],
                     "data": serializer.data}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def dispute_transaction(request, transaction_id: uuid.UUID):
    transaction = EscrowTransactions.objects.get(transaction_id=transaction_id)
    if transaction is None:
        response_data = {"status": status.HTTP_404_NOT_FOUND,
                         "status_description": "NOT FOUND",
                         "errors": {
                             "transaction_id": ["Transaction wasn't found"]
                         },
                         "data": {}}
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)

    if transaction.stage == TransactionStage.Completed:
        response_data = {"status": status.HTTP_406_NOT_ACCEPTABLE,
                         "status_description": "NOT ACCEPTABLE",
                         "errors": {
                             "transaction_id": ["Cannot refute transaction that was previously completed"]
                         },
                         "data": {}}
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
    user: User = request.user

    if user is None:
        raise ValidationError("User not found")
    if not request.user.is_authenticated:
        raise ValidationError("User is not authenticated")

    if user == transaction.from_user:
        transaction.from_user_confirmed = False
        transaction.from_user_confirmed_date = None
        transaction.stage = TransactionStage.Cancelled
        transaction.save()
    elif user == transaction.to_user:
        transaction.to_user_confirmed = False
        transaction.to_user_confirmed_date = None
        transaction.stage = TransactionStage.Cancelled
        transaction.save()
    else:
        response_data = {"status": status.HTTP_400_BAD_REQUEST,
                         "status_description": "BAD REQUEST",
                         "errors": {
                             "user_id": ["Logged In user is not part of the transaction"]
                         },
                         "data": {}}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    serializer = EscrowViewTransactionSerializer(transaction, many=False)
    response_data = {"status": status.HTTP_200_OK,
                     "status_description": "OK",
                     "errors": {
                     },
                     "data": serializer.data}
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_compliance_document():
    pass


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def search_users(request):
    name = request.GET.get("name", default="")
    if name != "":
        users = User.objects.filter(
            Q(first_name__contains=name) | Q(last_name__contains=name) | Q(username__contains=name))
        serializer = UserSerializer(users, many=True)
        return Response(
            {"status": status.HTTP_200_OK, "data": serializer.data, "status_description": "OK", "errors": []})
    else:
        return Response({"status": status.HTTP_200_OK, "data": [], "status_description": "OK"})
