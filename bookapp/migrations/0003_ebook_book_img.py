# Generated by Django 4.2.5 on 2023-09-18 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookapp", "0002_ebook_delete_book"),
    ]

    operations = [
        migrations.AddField(
            model_name="ebook",
            name="book_img",
            field=models.CharField(default="", max_length=200),
            preserve_default=False,
        ),
    ]
