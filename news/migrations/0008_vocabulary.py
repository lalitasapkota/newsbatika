# Generated by Django 5.0.4 on 2024-04-10 17:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0007_headline_vector"),
    ]

    operations = [
        migrations.CreateModel(
            name="vocabulary",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("word_vocab", models.TextField(null=True)),
                ("identifier", models.IntegerField(default=1)),
            ],
        ),
    ]
