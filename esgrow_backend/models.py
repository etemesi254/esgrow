import datetime
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class TransactionStage(models.TextChoices):
    Initiated = "Initiated", "Initiated"
    Pending = "Pending", "Pending"
    Completed = "Completed", "Completed"
    Cancelled = "Cancelled", "Cancelled"


# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField()
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)


class EscrowTransactions(models.Model):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    from_user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="+")
    to_user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="+")
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    stage = models.CharField(choices=TransactionStage.choices, max_length=200)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    # The time the transactions were reflected on user accounts
    # for purposes of accountability
    updated_on_users = models.BooleanField(default=False)
    time_updated_on_users = models.DateTimeField(null=True, auto_now_add=False)

    # whether the users have confirmed on their side
    from_user_confirmed = models.BooleanField(default=False)
    from_user_confirmed_date = models.DateTimeField(null=True)

    to_user_confirmed = models.BooleanField(default=False)
    to_user_confirmed_date = models.DateTimeField(null=True)


class MonetaryTransactions(models.Model):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    external_entity = models.CharField(max_length=200)
    external_reference = models.CharField(max_length=200, null=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    stage = models.CharField(choices=TransactionStage.choices, max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now_add=True)


class ComplianceDocuments(models.Model):
    # users in the system, party A and party B are users with contracts between
    # each other
    compliance_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    party_a = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='+')
    party_b = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="+")

    approved_by_party_a = models.BooleanField(default=False)
    party_a_date_approved = models.DateTimeField(default=None, null=True)
    approved_by_party_b = models.BooleanField(default=False)
    party_b_date_approved_date = models.DateTimeField(default=None, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    # the contract agreement files
    file = models.FileField()


class DisputeStage(models.TextChoices):
    Disputed = "Disputed", "Disputed"
    Resolved = "Resolved", "Resolved"
    Pending = "Pending", "Pending"


class Disputes(models.Model):
    dispute_id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    transaction_id = models.ForeignKey(EscrowTransactions, on_delete=models.RESTRICT,
                                       related_name="foreign_transaction_id")
    user_initiated = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="+")
    reason = models.CharField(max_length=300)
    stage = models.CharField(choices=DisputeStage.choices, max_length=200)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Signal request to create a user token

    See https://www.django-rest-framework.org/api-guide/authentication/#by-using-signals
    """
    if created:
        Token.objects.create(user=instance)


@receiver(pre_save, sender=EscrowTransactions)
def update_balance_on_transaction(sender, instance: EscrowTransactions, created=False, **kwargs):
    """
    Update the users balance when the transaction is complete
    """
    if (instance.amount > 0
            and instance.from_user_confirmed
            and instance.to_user_confirmed):
        # update user balances
        from_user = instance.from_user
        from_user.balance = from_user.balance - instance.amount
        from_user.save()

        to_user = instance.to_user
        to_user.balance = to_user.balance + instance.amount
        to_user.save()

        # Add date-times
        instance.updated_on_users = True
        instance.time_updated_on_users = instance.time_updated_on_users.now()

        instance.stage = TransactionStage.Completed
