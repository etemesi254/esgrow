# Generated by Django 5.0.1 on 2024-01-21 18:33

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("esgrow_backend", "0007_escrowtransactions_from_user_confirmed_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="amount",
            new_name="balance",
        ),
    ]
