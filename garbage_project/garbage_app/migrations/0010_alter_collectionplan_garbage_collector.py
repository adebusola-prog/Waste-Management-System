# Generated by Django 4.2 on 2023-05-09 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_alter_customuser_company_name"),
        ("garbage_app", "0009_collectionrequest_updated_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collectionplan",
            name="garbage_collector",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="my_plans",
                to="accounts.garbagecollector",
            ),
        ),
    ]