# Generated by Django 4.2 on 2023-05-08 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("garbage_app", "0008_alter_collectionrequest_rejection_reason"),
    ]

    operations = [
        migrations.AddField(
            model_name="collectionrequest",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]