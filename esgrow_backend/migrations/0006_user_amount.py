# Generated by Django 5.0.1 on 2024-01-21 16:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("esgrow_backend", "0005_alter_user_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="amount",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]