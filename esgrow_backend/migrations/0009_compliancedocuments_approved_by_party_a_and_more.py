# Generated by Django 5.0.1 on 2024-01-22 14:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("esgrow_backend", "0008_rename_amount_user_balance"),
    ]

    operations = [
        migrations.AddField(
            model_name="compliancedocuments",
            name="approved_by_party_a",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="compliancedocuments",
            name="approved_by_party_b",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="compliancedocuments",
            name="party_a_date_approved",
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="compliancedocuments",
            name="party_b_date_approved_date",
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
