# Generated by Django 5.0.1 on 2024-01-23 08:21

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("esgrow_backend", "0009_compliancedocuments_approved_by_party_a_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Disputes",
            fields=[
                (
                    "dispute_id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("reason", models.CharField(max_length=300)),
                (
                    "stage",
                    models.CharField(
                        choices=[
                            ("Disputed", "Disputed"),
                            ("Resolved", "Resolved"),
                            ("Pending", "Pending"),
                        ],
                        max_length=200,
                    ),
                ),
                (
                    "transaction_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="foreign_transaction_id",
                        to="esgrow_backend.escrowtransactions",
                    ),
                ),
                (
                    "user_initiated",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
