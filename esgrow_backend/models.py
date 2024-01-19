import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


# Create your models here.
class User(AbstractUser):
    email = models.EmailField()
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class EscrowTransactions(models.Model):
    class TransactionStage(models.TextChoices):
        Initiated = "Initiated", "Initiated"
        Pending = "Pending", "Pending"
        Completed = "Completed", "Completed"
        Cancelled = "Cancelled", "Cancelled"

    class TransactionType(models.TextChoices):
        Buyer = "Buyer", "Buyer"
        Seller = "Seller", "Seller"

    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    from_user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="+")
    to_user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="+")
    amount = models.DecimalField(max_digits=1000, decimal_places=100)
    stage = models.CharField(choices=TransactionStage.choices, max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


class MonetaryTransactions(models.Model):
    class TransactionStage(models.TextChoices):
        Initiated = "Initiated", "Initiated"
        Pending = "Pending", "Pending"
        Completed = "Completed", "Completed"
        Cancelled = "Cancelled", "Cancelled"

    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    external_entity = models.CharField(max_length=200)
    external_reference = models.CharField(max_length=200, null=True)
    amount = models.DecimalField(max_digits=1000, decimal_places=100)
    stage = models.CharField(choices=TransactionStage.choices, max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)


class ComplianceDocuments(models.Model):
    # users in the system, party A and party B are users with contracts between
    # each other
    compliance_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    party_a = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='+')
    party_b = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="+")

    created_date = models.DateTimeField(auto_now_add=True)
    # the contract agreement files
    file = models.FileField()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Signal request to create a user token

    See https://www.django-rest-framework.org/api-guide/authentication/#by-using-signals
    """
    if created:
        Token.objects.create(user=instance)
